"""학교 조직 구조를 관리하는 모듈"""

from typing import Dict, Optional, List, Union
from collections import deque

from pydantic import BaseModel

from crawler import settings


class OrganizationUnit(BaseModel):
    """조직의 기본 단위 (전화번호, URL 등 포함)
    
    Attributes:
        name (str): 조직 이름
        phone (Optional[str]): 전화번호
        url (Optional[str]): URL, 홈페이지 주소
    """

    name: str
    phone: Optional[str] = None
    url: Optional[str] = None


class OrganizationGroup(BaseModel):
    """하위 조직을 포함할 수 있는 조직 단위 (대학본부, 단과대학 등)"""

    name: str
    subunits: Dict[str, Union["OrganizationUnit", "OrganizationGroup"]] = {}

    def add_subunit(
        self, subunit_name: str, subunit: Union["OrganizationUnit", "OrganizationGroup"]
    ):
        """하위 조직 추가"""
        self.subunits[subunit_name] = subunit

    def __iter__(self):
        return iter(self.subunits.values())

    def as_list(self) -> List[Union["OrganizationUnit", "OrganizationGroup"]]:
        """하위 조직을 리스트로 반환"""
        return list(self.subunits.values())


class UniversityStructure(BaseModel):
    """학교 전체 조직 구조를 관리하는 클래스"""

    root: Union[OrganizationGroup, OrganizationUnit]

    @classmethod
    def from_dict(cls, data: Dict) -> "UniversityStructure":
        """JSON 데이터를 Pydantic 모델로 변환"""
        return cls(root=cls._parse_data("Root", data))

    @classmethod
    def _parse_data(
        cls, name: str, data: Dict
    ) -> Union[OrganizationGroup, OrganizationUnit]:
        """재귀적으로 데이터를 파싱하여 Pydantic 모델로 변환"""
        if "phone" in data or "url" in data:
            return OrganizationUnit(
                name=name, phone=data.get("phone"), url=data.get("url")
            )
        else:
            subunits = {key: cls._parse_data(key, value) for key, value in data.items()}
            return OrganizationGroup(name=name, subunits=subunits)

    def get_unit(
        self, query: str
    ) -> Union[
        OrganizationUnit, List[Union[OrganizationUnit, OrganizationGroup]], None
    ]:
        """조직 구조에서 해당하는 부분을 찾아 반환

        Args:
            query (str): 찾고자 하는 조직의 경로
                /로 구분된 경로를 입력하며, 상위 조직부터 하위 조직까지 순차적으로 입력
                예) "단과대학/SW대학/컴퓨터공학부"

        Returns:
            Union[OrganizationUnit, List[Union[OrganizationUnit, OrganizationGroup]], None]:
                해당하는 조직을 찾은 경우 해당 조직을 반환
                찾은 조직이 OrganizationGroup인 경우 하위 조직을 리스트로 반환
                찾지 못한 경우 None 반환
        """
        parts = query.strip("/").split("/")  # '/'가 끝에 있으면 제거 후 분리
        return self._bfs_search(self.root, parts)

    def _bfs_search(
        self, current_node: Union[OrganizationGroup, OrganizationUnit], parts: List[str]
    ) -> Union[
        OrganizationUnit, List[Union[OrganizationUnit, OrganizationGroup]], None
    ]:
        """BFS 방식으로 각 part를 순차적으로 탐색

        BFS 방식으로 각 part를 순차적으로 탐색하여 조직 구조를 찾는 함수입니다.
        이 함수는 주어진 현재 노드에서 시작하여 남은 경로(parts)를 BFS 방식으로 탐색합니다.
        각 단계에서 현재 노드가 OrganizationGroup인 경우 하위 유닛에서 다음 경로를 찾고,
        그렇지 않은 경우 트리 전체에서 이름으로 탐색합니다.

        Args:
            current_node (Union[OrganizationGroup, OrganizationUnit]): 현재 노드
            parts (List[str]): 남은 경로

        Returns:
            Union[OrganizationUnit, List[Union[OrganizationUnit, OrganizationGroup]], None]:
                해당하는 조직을 찾은 경우 해당 조직을 반환
                찾은 조직이 OrganizationGroup인 경우 하위 조직을 리스트로 반환
                찾지 못한 경우 None 반환
        """

        queue = deque([(current_node, parts)])  # (현재 노드, 남은 parts)

        while queue:
            node, remaining_parts = queue.popleft()  # 큐에서 노드 꺼내기

            # 경로가 모두 탐색된 경우, 현재 노드를 반환
            if not remaining_parts:
                return node if isinstance(node, OrganizationUnit) else node.as_list()

            # 현재 노드가 OrganizationGroup인 경우 하위 유닛에서 찾기
            if isinstance(node, OrganizationGroup):
                part = remaining_parts[0]  # 현재 찾고 있는 부분

                # 하위 유닛에서 찾기
                if part in node.subunits:
                    queue.append(
                        (node.subunits[part], remaining_parts[1:])
                    )  # 하위 유닛으로 재귀적 탐색
                else:
                    # 하위 유닛에 없는 경우, 트리 전체에서 이름으로 탐색
                    candidates = self._search_by_name(self.root, part)

                    for candidate in candidates:
                        queue.append(
                            (candidate, remaining_parts[1:])
                        )  # 재귀적으로 나머지 part 탐색

        return None  # 찾지 못한 경우 None 반환

    def _search_by_name(
        self, node: Union[OrganizationGroup, OrganizationUnit], query: str
    ) -> List[Union[OrganizationUnit, OrganizationGroup]]:
        """이름 기반 전체 검색 (트리 순회)"""
        results = []
        if node.name == query:
            results.append(node)

        if isinstance(node, OrganizationGroup):
            for subunit in node.subunits.values():
                results.extend(self._search_by_name(subunit, query))

        return results

def get_tukorea_structure() -> UniversityStructure:
    """한국공학대학교 조직 구조를 반환"""
    return UniversityStructure.from_dict(settings.SCHOOL_INFO())


if __name__ == "__main__":
    # 학교 조직 구조를 불러옴
    school_structure = UniversityStructure.from_dict(settings.SCHOOL_INFO())

    print(school_structure.get_unit("단과대학/SW대학/컴퓨터공학부"))
    print(school_structure.get_unit("컴퓨터공학부"))  # 단독 검색 가능
    print(school_structure.get_unit("SW대학/컴퓨터공학부"))  # 상위 구조 일부 포함 가능
    print(school_structure.get_unit("단과대학/컴퓨터공학부"))  # 부분 포함 가능
