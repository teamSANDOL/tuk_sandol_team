# Nginx Proxy Manager 임시 이전 런북

Cloudflare Tunnel(cloudflared)의 접속 지연 문제 때문에 외부 진입점을 Nginx Proxy
Manager(NPM)로 **임시 이전**하는 절차입니다. 터널을 다시 쓸 수 있게 되면 즉시 되돌립니다.
두 경로는 계속 살려 두고, 오가는 일은 Cloudflare DNS 레코드 교체만으로 끝냅니다.
이 문서는 `sandori.kr`만 다룹니다. 게이트웨이 `server_name`에 있는 다른
호스트네임은 이 전환의 대상이 아닙니다.

## 1. 개요

### 결정 사항

- 게이트웨이는 cloudflared(CT110, CT131)와 NPM(CT114) 세 프록시를 **동시에** 신뢰합니다. 모드 전환에 게이트웨이 설정 변경이나 reload가 필요 없습니다.
- NPM 모드에서 Cloudflare DNS는 DNS-only(회색 구름)로 둡니다.
- NPM 모드의 `sandori.kr`은 `CNAME house.sio2.kr`입니다. apex CNAME은 Cloudflare가 flattening으로 처리합니다.
- `house.sio2.kr`은 pve1의 CT105 `favonia/cloudflare-ddns`가 `PROXIED=false`로 갱신합니다.
- NPM은 pve1의 별도 LXC CT114(`172.30.1.114`)에 Docker로 띄웁니다. 이미지는 `jc21/nginx-proxy-manager:2.16.0`으로 고정합니다.
- 공유기에서 80/443을 `172.30.1.114`로 포워딩합니다.
- NPM은 `http://172.30.1.108:8010`(CT108 `sandol-gateway`)로 프록시합니다.
- 문서·관리 경로의 보호는 모드마다 다릅니다. 터널 모드는 Cloudflare Access, NPM 모드는 NPM Access List(Basic Auth)입니다. 자세한 내용은 9번을 봅니다.

### 구조

터널 모드 (평상시):

```text
사용자 --HTTPS--> Cloudflare 엣지(proxied, Access)
                        |  터널
                        v
     cloudflared (CT110 172.30.1.110 / CT131 172.30.1.75)
                        |
                        v
        sandol-gateway (CT108 172.30.1.108:8010) --> 각 서비스
```

NPM 모드 (임시):

```text
사용자 --DNS: sandori.kr -> house.sio2.kr -> 집 공인 IP (DNS only)
   |
   v
공유기 80/443 포워딩
   |
   v
NPM (CT114 172.30.1.114)   TLS 종료, Access List
   |  http, X-Forwarded-For 끝에 실제 접속 IP를 덧붙임
   v
sandol-gateway (CT108 172.30.1.108:8010) --> 각 서비스
```

### 게이트웨이의 실제 IP 판별

`sandol-gateway/gateway/00-limits.conf`는 다음처럼 설정합니다.

```nginx
set_real_ip_from 172.30.1.110;   # cloudflared CT110
set_real_ip_from 172.30.1.75;    # cloudflared CT131
set_real_ip_from 172.30.1.114;   # NPM CT114
real_ip_header   X-Forwarded-For;
real_ip_recursive on;
```

- 두 프록시 모두 `X-Forwarded-For`(XFF) 맨 끝에 자신이 직접 본 접속 IP를 덧붙입니다.
  NPM v2.16.0은 `$proxy_add_x_forwarded_for`를 쓰고, Cloudflare는 기존 XFF가 있으면 덮어쓰지 않고 뒤에 append합니다.
  운영 로그에서 평소 요청의 XFF는 `cf_ip` 한 개였으므로 cloudflared는 자기 IP를 추가하지 않습니다.
- 클라이언트는 XFF의 앞쪽 값만 조작할 수 있습니다. `real_ip_recursive on`이면 신뢰 목록의 주소를 오른쪽부터 건너뛰고
  처음 만나는 비신뢰 값을 클라이언트 IP로 쓰므로, 앞에 끼워 넣은 위조 값은 무시됩니다.
- `X-Real-IP`(Cloudflare가 제거)와 `CF-Connecting-IP`(NPM이 보내지 않음)는 두 경로에 모두 있지 않아서 쓰지 않습니다.
  `real_ip_header`는 하나만 지정할 수 있습니다.
- 프록시가 바뀌면 `set_real_ip_from` 줄만 수정하면 됩니다.
- 원래 연결 주소(프록시 IP)는 로그의 `proxy_addr`에 남습니다. 그래서 어느 경로로 들어왔는지 알 수 있습니다.

### 공개 경로

| 경로 | 대상 서비스 | 비고 |
| --- | --- | --- |
| `/` | 게이트웨이 정적 랜딩 | 랜딩, `/owner-guide/`, `/login-complete/` 포함 |
| `/auth/` | Keycloak | |
| `/relay/` | auth-relay | `/relay/docs`, `/relay/redoc`, `/relay/openapi.json`은 잠금 |
| `/kakao-bot/` | 카카오 봇 서비스 | 스킬 웹훅은 공개. 문서와 `/kakao-bot/admin`은 잠금 |
| `/meal/` | 학식 API | 문서만 잠금 |
| `/meal-web/` | 학식 웹 | 문서와 `/meal-web/admin`은 잠금 |
| `/static-info/` | 정적 정보 API | 문서만 잠금 |
| `/notice-notification/` | 공지 알림(NestJS) | `/doc`, `/doc-json`만 잠금 |
| `/classroom-timetable/` | 강의실 시간표 | |
| `/grafana/` | Grafana | 자체 로그인 사용. WebSocket(Grafana Live) 필요 |

## 2. CT114 준비

1. pve1에서 LXC CT114를 만들고 IP를 `172.30.1.114`로 고정합니다. Docker를 쓰려면 LXC의 `nesting` 기능을 켭니다.
2. CT114에 Docker와 compose 플러그인을 설치합니다.
3. 작업 디렉터리(예: `/opt/npm`)에 `docker-compose.yml`과 빈 파일 `empty-ip_ranges.conf`를 만듭니다.
   빈 파일은 아래 `IP_RANGES_FETCH_ENABLED` 설명의 이유로 씁니다.

```bash
mkdir -p /opt/npm && cd /opt/npm
touch empty-ip_ranges.conf
```

```yaml
services:
  npm:
    image: jc21/nginx-proxy-manager:2.16.0
    container_name: npm
    restart: unless-stopped
    ports:
      - "80:80"     # HTTP (공유기 포워딩)
      - "443:443"   # HTTPS (공유기 포워딩)
      - "81:81"     # 관리 UI. LAN 전용, 공유기에서 포워딩하지 않는다
    environment:
      IP_RANGES_FETCH_ENABLED: "false"
      # DISABLE_IPV6: "true"   # IPv6를 쓰지 않는 환경에서만 켠다
    volumes:
      - ./data:/data
      - ./letsencrypt:/etc/letsencrypt
      # NPM이 Cloudflare·CloudFront 대역을 다시 써 넣지 못하게 빈 파일로 덮는다
      - ./empty-ip_ranges.conf:/etc/nginx/conf.d/include/ip_ranges.conf:ro
```

```bash
docker compose up -d
```

- 81번 포트(관리 UI)는 LAN 전용입니다. 공유기 포워딩은 80/443만 걸고 81은 걸지 않습니다.
- 첫 접속(`http://172.30.1.114:81`)에서 기본 관리자 계정을 바로 자기 계정으로 바꿉니다.
- `IP_RANGES_FETCH_ENABLED: "false"`를 넣는 이유: NPM 기본 `nginx.conf`는 Cloudflare·CloudFront
  대역을 `set_real_ip_from`으로 신뢰하고 `real_ip_header`를 `X-Real-IP`로 씁니다.
  DNS-only 환경에서는 CloudFront 배포나 Cloudflare Worker를 거쳐 origin에 붙는
  방식으로 `X-Real-IP`를 위조할 수 있습니다. 환경 변수를 켜면 신뢰 목록이 사설 대역(10/8, 172.16/12, 192.168/16)으로 한정됩니다.
- 빈 `ip_ranges.conf`를 읽기 전용으로 마운트하는 이유: v2.16.0에서 이 환경 변수는 **기동 시 1회 fetch만** 건너뜁니다.
  6시간마다 도는 갱신 타이머는 남아 있어서(`backend/index.js`, `backend/internal/ip_ranges.js`), 변수만 쓰면 몇 시간 뒤
  대역이 다시 채워집니다. 테스트 서버에서 v2.16.0으로 확인했을 때 타이머와 같은 fetch를 호출하자 `ip_ranges.conf`에
  `set_real_ip_from` 265줄이 생겼고, 읽기 전용 빈 파일을 마운트한 쪽은 `EROFS` 경고만 남기고 파일이 빈 채로 유지되었습니다(기동과 `nginx -t`도 정상).
  로그에 `Could not write ... EROFS` 경고가 주기적으로 나오는 것은 정상입니다.
- 기동 후 확인: 결과가 `0`이어야 합니다. 0이 아니면 마운트가 빠진 것입니다.

  ```bash
  docker exec npm grep -c set_real_ip_from /etc/nginx/conf.d/include/ip_ranges.conf
  ```
- `DISABLE_IPV6`는 필요할 때만 씁니다. 기본은 주석 처리 상태로 둡니다.
- 볼륨은 `./data`(설정, Access List, 로그)와 `./letsencrypt`(인증서)입니다. 둘 다 백업 대상입니다.

## 3. Access List 만들기

NPM 관리 UI의 Access Lists에서 새로 만듭니다.

1. 이름: `teamSANDOL-docs` (예시)
2. Authorization 탭에서 Basic Auth 사용자를 등록합니다. 팀원별로 계정을 나누면 회수가 쉽습니다.
3. IP 규칙(Access 탭)은 넣지 않습니다. 그래서 Satisfy Any / Satisfy All 선택은 결과에 영향이 없습니다.
4. 저장한 뒤 목록에서 이 Access List의 **ID**를 확인합니다. 인증 파일은 CT114 안의 `/data/access/<ID>`에 생깁니다.
   이 ID를 6번 Advanced 스니펫의 `<ID>` 자리에 넣습니다.

이 Access List는 Proxy Host의 Access List 드롭다운에 연결하지 않습니다. 6번 스니펫이 파일 경로로 직접 참조합니다.

## 4. SSL 인증서

Let's Encrypt **DNS Challenge(Cloudflare)** 로 `sandori.kr` 인증서를 발급합니다.

1. Cloudflare에서 API 토큰을 만듭니다. 권한은 `Zone:DNS:Edit`, 대상 리소스는 `sandori.kr` 존 하나로 한정합니다.
2. NPM의 SSL Certificates에서 Add Let's Encrypt Certificate를 고르고 도메인에 `sandori.kr`을 넣습니다.
3. Use a DNS Challenge를 켜고 DNS Provider로 Cloudflare를 선택한 뒤 토큰을 붙여 넣습니다.
   토큰은 문서, 채팅, 로그에 남기지 않습니다.

**NPM 모드로 넘어가기 전에 발급해야 합니다.** HTTP-01 방식은 Let's Encrypt가 `sandori.kr:80`으로 검증하러 오는데,
전환 전에는 DNS가 아직 터널을 가리키고 있어 NPM에 닿지 않아 실패합니다. DNS Challenge는 TXT 레코드만
쓰므로 DNS 전환 여부와 무관하게 발급되고, 이후 갱신도 같은 방식으로 됩니다.
터널 모드로 돌아가 있는 동안에도 갱신은 그대로 동작하므로, 다시 NPM 모드로 갈 때 인증서가 만료되어 있을 일은 없습니다.

## 5. Proxy Host 설정

Proxy Hosts에서 새 호스트를 만듭니다.

| 항목 | 값 |
| --- | --- |
| Domain Names | `sandori.kr` |
| Scheme | `http` |
| Forward Hostname / IP | `172.30.1.108` |
| Forward Port | `8010` |
| Websockets Support | 켠다 (Grafana Live) |
| Block Common Exploits | 끈다 |
| Access List | Publicly Accessible |
| SSL Certificate | 4번에서 발급한 인증서 |
| Force SSL | 켠다 |
| HTTP/2 Support | 켠다 |
| HSTS | NPM 모드가 안정된 뒤 켠다 |

- Block Common Exploits를 끄는 이유: 정상 쿼리 문자열(Keycloak의 긴 `state`, 검색어 등)을 공격으로 오탐할 수 있습니다.
- Access List를 Publicly Accessible로 두는 이유: 호스트 전체에 걸면 카카오 웹훅(`/kakao-bot/`)과 Keycloak 로그인 흐름이 막힙니다. 잠글 경로는 6번에서 경로 단위로 지정합니다.
- HSTS는 되돌리기 어렵습니다. NPM 모드로 며칠 안정된 것을 확인한 다음에 켭니다. 터널 모드도 HTTPS라 충돌하지는 않습니다.

## 6. Advanced 탭 스니펫

Proxy Host의 Advanced 탭 Custom Nginx Configuration에 넣습니다. `<ID>`는 3번에서 확인한 Access List ID로 바꿉니다.

```nginx
# 문서·관리 경로만 팀 Basic Auth로 잠근다 (NPM 모드에서 Cloudflare Access 역할)
location ~ ^/(?:(?:kakao-bot|meal|meal-web|relay|static-info)/(?:docs|redoc|openapi\.json)|notice-notification/doc|kakao-bot/admin|meal-web/admin) {
    auth_basic           "Sandol internal";
    auth_basic_user_file /data/access/<ID>;
    proxy_set_header     Authorization "";   # 팀 비밀번호를 업스트림에 넘기지 않는다
    include conf.d/include/proxy.conf;
}
```

- `include conf.d/include/proxy.conf` 안의 `proxy_set_header`와 `proxy_pass`가 같은 `location`에 있으므로 `Authorization` 제거 줄과 공존합니다.
- 이 `location`에서는 server 레벨의 `Upgrade` / `Connection` 헤더 설정이 상속되지 않습니다. 문서·관리 경로에는 WebSocket이 필요 없으므로 문제가 없습니다.
- 정규식 `location`은 NPM이 만든 `location /`(접두사 매칭)보다 우선합니다.

### 잠기는 경로

| 서비스 | 경로 | 개수 |
| --- | --- | --- |
| FastAPI 5개 (`kakao-bot`, `meal`, `meal-web`, `relay`, `static-info`) | 각 `/<서비스>/docs`, `/<서비스>/redoc`, `/<서비스>/openapi.json` | 15 |
| NestJS `notice-notification` | `/notice-notification/doc` (`/doc-json` 포함, 접두사 매칭) | 1 |
| 관리 UI | `/kakao-bot/admin`, `/meal-web/admin` | 2 |

정규식 끝을 고정하지 않았으므로 `/meal/docs/oauth2-redirect`, `/notice-notification/doc-json`처럼
접두사가 같은 하위 경로도 함께 잠깁니다.

> **경고: 처음 NPM 모드로 넘어가기 전에 보호 경로 목록을 대조합니다.**
> 현재 Cloudflare Access 앱 "Sandori Swagger (teamSANDOL)"의 보호 경로 목록(18개)과 위 표를
> 하나씩 맞춰 보고, 표에서 빠진 경로가 없는지 확인합니다. 18 = 문서 16 + 관리 2로 추정하지만
> 아직 확인하지 않았습니다. 문서 16과 이 표의 15+1이 일치하는지도 함께 봅니다. 빠진 경로가 있으면
> 전환 전에 정규식에 추가합니다. NPM 모드에서는 그 경로가 인증 없이 공개됩니다.

## 7. 전환 전 검증

DNS는 터널 모드인 상태에서 LAN의 PC나 서버에서 확인합니다. `--resolve`로 `sandori.kr`을
NPM(`172.30.1.114`)에 직접 붙입니다. 인증서 검증을 그대로 두어 4번의 인증서도 함께 확인합니다.

```bash
R="--resolve sandori.kr:443:172.30.1.114"

curl -s -o /dev/null -w "%{http_code}\n" $R https://sandori.kr/
curl -s -o /dev/null -w "%{http_code}\n" $R https://sandori.kr/kakao-bot/health
curl -s -o /dev/null -w "%{http_code}\n" $R https://sandori.kr/meal/docs
curl -s -o /dev/null -w "%{http_code}\n" $R -u "<사용자>:<비밀번호>" https://sandori.kr/meal/docs
curl -s -o /dev/null -w "%{http_code}\n" $R https://sandori.kr/meal/health
curl -s $R https://sandori.kr/auth/realms/Sandori/.well-known/openid-configuration | python -c "import json,sys; print(json.load(sys.stdin)['issuer'])"
curl -s -o /dev/null -w "%{http_code}\n" $R https://sandori.kr/notice-notification/doc-json
```

| 요청 | 기대값 |
| --- | --- |
| `/` | 200 |
| `/kakao-bot/health` | 200 |
| `/meal/docs` | 401 |
| `/meal/docs` (Basic Auth 포함) | 200 |
| `/meal/health` | 200 (잠금 대상 아님) |
| `/auth/realms/Sandori/.well-known/openid-configuration`의 `issuer` | `https://sandori.kr/auth/realms/Sandori` |
| `/notice-notification/doc-json` | 401 |

외부망(휴대폰 LTE 등, Wi-Fi 끔)에서도 공인 IP의 443이 열려 있는지 확인합니다. DNS가 아직 터널을
가리키므로 도메인 대신 IP로 붙습니다.

```bash
curl -sk -o /dev/null -w "%{http_code}\n" --resolve sandori.kr:443:<집 공인 IP> https://sandori.kr/
```

공유기 포워딩이나 통신사 포트 차단이 있으면 여기서 걸립니다. LAN 안에서 공인 IP로 붙는 시험은
공유기의 hairpin NAT 지원 여부에 따라 실패할 수 있으므로 외부망에서 확인합니다.

## 8. 사전 준비

1. **터널 정보 기록.** Zero Trust 대시보드에서 터널 ID와 `sandori.kr` public hostname 설정(서비스 URL, 경로, 옵션)을 기록해 둡니다.
   NPM → 터널 전환에서 `<tunnel-id>.cfargotunnel.com`이 필요합니다.
2. **게이트웨이 설정 반영.** 게이트웨이는 cloudflared와 NPM을 모두 받으므로 언제 배포해도 됩니다.
   모드 전환 시점에 맞출 필요가 없습니다. CT108에서 서브모듈을 갱신하고 문법을 확인한 뒤 reload합니다.

   ```bash
   git pull
   git submodule update --init sandol-gateway
   docker exec sandol-gateway openresty -t && docker exec sandol-gateway openresty -s reload
   ```

   게이트웨이 `gateway/` 디렉터리는 볼륨 마운트(`./sandol-gateway/gateway:/etc/nginx/conf.d`)라
   이미지를 다시 빌드할 필요가 없습니다. 이 반영 이후로는 모드를 바꿔도 게이트웨이를 건드리지 않습니다.
3. 2번(CT114), 3번(Access List), 4번(인증서), 5~6번(Proxy Host), 7번(전환 전 검증)을 끝냅니다.

## 9. 모드 전환

전환은 Cloudflare DNS에서 `sandori.kr` 레코드 하나를 바꾸는 것으로 끝납니다.
게이트웨이 설정 변경, reload, 서비스 재기동은 필요 없습니다.

### 터널 → NPM

Cloudflare DNS에서 `sandori.kr`의 터널 레코드를 다음으로 바꿉니다.

| 항목 | 값 |
| --- | --- |
| 타입 / 이름 | `CNAME` / `sandori.kr` |
| 대상 | `house.sio2.kr` |
| 프록시 | DNS only (회색 구름) |
| TTL | 60초 |

### NPM → 터널

같은 레코드를 되돌립니다.

| 항목 | 값 |
| --- | --- |
| 타입 / 이름 | `CNAME` / `sandori.kr` |
| 대상 | `<tunnel-id>.cfargotunnel.com` (8번 1단계에서 기록한 값) |
| 프록시 | Proxied (주황 구름) |
| TTL | Auto |

### 전환이 퍼지는 시간

- 터널 → NPM: 기존 Proxied 레코드의 TTL은 Auto(300초)라서 리졸버 캐시 때문에 최대 약 5분 동안 일부 사용자가 옛 경로(터널)로 들어옵니다.
- NPM → 터널: 새 레코드의 TTL이 60초이므로 최대 약 1분입니다.
- 퍼지는 동안 사용자에 따라 두 경로로 나뉘어 들어옵니다. 게이트웨이가 두 경로를 모두 받고 같은 서비스를 바라보므로 서비스에는 영향이 없습니다.

### NPM 모드에서도 유지할 것

NPM 모드 동안에도 다음을 **삭제하지 않고 그대로 둡니다.** 터널로 즉시 복귀하기 위한 조건입니다.

- 터널의 `sandori.kr` public hostname 라우트
- cloudflared CT110, CT131
- Cloudflare Access 앱 "Sandori Swagger (teamSANDOL)"
- Keycloak의 `cloudflare-access` 클라이언트

### 모드별 보호 방식

- **터널 모드**: Cloudflare Access가 문서·관리 경로를 보호합니다.
- **NPM 모드**: DNS-only라 Access가 효력이 없습니다. 6번 스니펫의 NPM Lock(Basic Auth)이 보호합니다.
- **터널 모드에서도** 공유기 443 포워딩과 NPM이 살아 있으면 공인 IP로 NPM에 직접 접근할 수 있습니다.
  이 경로는 Cloudflare Access를 거치지 않으므로 NPM Lock이 막습니다. 터널 모드로 오래 머물 계획이면
  공유기의 80/443 포워딩을 끄는 선택지도 있습니다. 끄면 다음 NPM 모드 전에 다시 켜야 합니다.
- NPM 인증서는 DNS-01이라 터널 모드에서도 계속 갱신됩니다(4번).

## 10. 전환 후 검증

- 게이트웨이 JSON 로그에서 `remote_addr`와 `proxy_addr`를 봅니다.

  ```bash
  docker logs --tail 20 sandol-gateway
  ```

  | 모드 | `proxy_addr` | `remote_addr` |
  | --- | --- | --- |
  | NPM | `172.30.1.114` | 실제 클라이언트 공인 IP |
  | 터널 | `172.30.1.110` 또는 `172.30.1.75` | 실제 클라이언트 공인 IP |

  `cf_ray`, `colo`, `cf_country`, `cf_ip` 필드는 NPM 모드에서 빈 값이고 터널 모드에서 채워지는 것이 정상입니다.
  전파 중에는 두 종류가 섞여 보일 수 있습니다.
- 카카오 스킬을 실제로 호출해 봇이 응답하는지 확인합니다.
- Keycloak 로그인(`/auth/`)이 끝까지 되는지 확인합니다.
- Grafana(`/grafana/`)에 접속하고 실시간 패널이 갱신되는지 확인합니다.
- 7번 표의 문서 경로 401 / 200 결과가 실제 도메인에서도 같은지 봅니다. 터널 모드에서는 Cloudflare Access 로그인 화면이 먼저 나옵니다.

## 11. 남는 한계

- NPM 모드에서는 집 공인 IP가 DNS에 노출됩니다.
- NPM 모드에서는 Cloudflare의 DDoS 보호와 WAF가 없습니다.
- 공인 IP가 바뀌면 DDNS(CT105)가 반영할 때까지 NPM 모드에서 순단이 있습니다.
- 터널 모드에서도 포워딩이 열려 있으면 공인 IP로 NPM에 직접 닿을 수 있습니다(9번).
