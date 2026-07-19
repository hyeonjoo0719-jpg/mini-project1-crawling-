from __future__ import annotations

import csv
import io
import string
from typing import Any

import requests
from flask import Flask, Response, render_template, request

app = Flask(__name__)

API_BASE = "https://www.thecocktaildb.com/api/json/v1/1"

KOREAN_INGREDIENT_MAP = {
    "보드카": "Vodka",
    "시트론보드카": "Citron vodka",
    "크랜베리보드카": "Cranberry vodka",
    "바닐라보드카": "Vanilla vodka",
    "진": "Gin",
    "럼": "Rum",
    "화이트럼": "White rum",
    "다크럼": "Dark rum",
    "골드럼": "Gold rum",
    "스파이스드럼": "Spiced rum",
    "코코넛럼": "Coconut rum",
    "아네호럼": "Añejo rum",
    "카샤사": "Cachaca",
    "위스키": "Whiskey",
    "버번": "Bourbon",
    "스카치": "Scotch",
    "블렌디드스카치": "Blended Scotch",
    "아이리시위스키": "Irish whiskey",
    "라이위스키": "Rye",
    "캐네디안위스키": "Canadian whisky",
    "테킬라": "Tequila",
    "골드테킬라": "Gold Tequila",
    "메스칼": "Mezcal",
    "브랜디": "Brandy",
    "코냑": "Cognac",
    "애플브랜디": "Apple brandy",
    "체리브랜디": "Cherry brandy",
    "애프리콧브랜디": "Apricot brandy",
    "압생트": "Absinthe",
    "삼부카": "Sambuca",
    "그레인알코올": "Grain Alcohol",
    "에버클리어": "Everclear",
    "와인": "Wine",
    "레드와인": "Red wine",
    "화이트와인": "White Wine",
    "로제와인": "Rose wine",
    "스파클링와인": "Sparkling wine",
    "샴페인": "Champagne",
    "베르무트": "Vermouth",
    "드라이베르무트": "Dry Vermouth",
    "스위트베르무트": "Sweet Vermouth",
    "화이트베르무트": "White Vermouth",
    "셰리": "Sherry",
    "포트와인": "Port",
    "사케": "Sake",
    "트리플섹": "Triple Sec",
    "쿠앵트로": "Cointreau",
    "그랑마니에르": "Grand Marnier",
    "아마레토": "Amaretto",
    "깔루아": "Kahlua",
    "베일리스": "Baileys",
    "캄파리": "Campari",
    "아페롤": "Aperol",
    "그린샤르트뢰즈": "Green Chartreuse",
    "옐로우샤르트뢰즈": "Yellow Chartreuse",
    "프랑젤리코": "Frangelico",
    "예거마이스터": "Jägermeister",
    "드람뷔": "Drambuie",
    "갈리아노": "Galliano",
    "미도리": "Midori",
    "말리부": "Malibu",
    "블루큐라소": "Blue Curacao",
    "크렘드카카오": "Creme de Cacao",
    "크렘드카시스": "Creme de Cassis",
    "크렘드민트": "Creme de Menthe",
    "화이트크렘드민트": "White Creme de Menthe",
    "그린크렘드민트": "Green Creme de Menthe",
    "체리헤링": "Cherry Heering",
    "두보네": "Dubonnet",
    "사우던컴포트": "Southern Comfort",
    "슈납스": "Schnapps",
    "바나나리큐어": "Banana liqueur",
    "커피리큐어": "Coffee liqueur",
    "초콜릿리큐어": "Chocolate liqueur",
    "코코넛리큐어": "Coconut Liqueur",
    "헤이즐넛리큐어": "Hazelnut liqueur",
    "바닐라리큐어": "Vanilla liqueur",
    "샹보르": "Chambord",
    "어드보카트": "Advocaat",
    "콜라": "Coca-Cola",
    "사이다": "7-Up",
    "스프라이트": "Sprite",
    "진저에일": "Ginger Ale",
    "진저비어": "Ginger beer",
    "탄산수": "Soda water",
    "토닉워터": "Tonic water",
    "에너지드링크": "Energy drink",
    "레모네이드": "Lemonade",
    "오렌지주스": "Orange juice",
    "크랜베리주스": "Cranberry juice",
    "파인애플주스": "Pineapple juice",
    "자몽주스": "Grapefruit juice",
    "라임주스": "Lime juice",
    "레몬주스": "Lemon juice",
    "애플주스": "Apple juice",
    "포도주스": "Grape juice",
    "토마토주스": "Tomato Juice",
    "구아바주스": "Guava juice",
    "그레나딘": "Grenadine",
    "설탕시럽": "Sugar syrup",
    "바닐라시럽": "Vanilla syrup",
    "레몬": "Lemon",
    "라임": "Lime",
    "오렌지": "Orange",
    "자몽": "Grapefruit",
    "파인애플": "Pineapple",
    "크랜베리": "Cranberry",
    "체리": "Cherry",
    "딸기": "Strawberry",
    "바나나": "Banana",
    "키위": "Kiwi",
    "복숭아": "Peach",
    "라즈베리": "Raspberry",
    "블랙베리": "Blackberry",
    "수박": "Watermelon",
    "포도": "Grape",
    "토마토": "Tomato",
    "올리브": "Olive",
    "생강": "Ginger",
    "민트": "Mint",
    "바질": "Basil",
    "오이": "Cucumber",
    "우유": "Milk",
    "생크림": "Cream",
    "헤비크림": "Heavy cream",
    "코코넛크림": "Cream of Coconut",
    "요거트": "Yoghurt",
    "커피": "Coffee",
    "에스프레소": "Espresso",
    "초콜릿": "Chocolate",
    "초콜릿시럽": "Chocolate syrup",
    "코코아파우더": "Cocoa powder",
    "바닐라": "Vanilla",
    "계란": "Egg",
    "계란흰자": "Egg White",
    "계란노른자": "Egg Yolk",
    "설탕": "Sugar",
    "꿀": "Honey",
    "소금": "Salt",
    "비터스": "Bitters",
    "앙고스투라비터스": "Angostura bitters",
    "얼음": "Ice",
    "맥주": "Beer",
    "에일": "Ale",
    "기네스": "Guinness",
}

KOREAN_COCKTAIL_NAME_MAP = {
    "마티니": "Martini",
    "더티마티니": "Dirty Martini",
    "애플티니": "Appletini",
    "초콜릿마티니": "Chocolate Martini",
    "에스프레소마티니": "Espresso Martini",
    "마가리타": "Margarita",
    "모히토": "Mojito",
    "맨해튼": "Manhattan",
    "올드패션드": "Old Fashioned",
    "네그로니": "Negroni",
    "다이키리": "Daiquiri",
    "다이커리": "Daiquiri",
    "헤밍웨이다이키리": "Hemingway Daiquiri",
    "코스모폴리탄": "Cosmopolitan",
    "블러디메리": "Bloody Mary",
    "피나콜라다": "Pina Colada",
    "위스키사워": "Whiskey Sour",
    "아마레토사워": "Amaretto Sour",
    "미도리사워": "Midori Sour",
    "데킬라선라이즈": "Tequila Sunrise",
    "마이타이": "Mai Tai",
    "롱아일랜드아이스티": "Long Island Iced Tea",
    "스크류드라이버": "Screwdriver",
    "모스크뮬": "Moscow Mule",
    "진토닉": "Gin and Tonic",
    "진피즈": "Gin Fizz",
    "슬로우진피즈": "Sloe Gin Fizz",
    "사이드카": "Sidecar",
    "사제락": "Sazerac",
    "에비에이션": "Aviation",
    "쿠바리브레": "Cuba Libre",
    "미모사": "Mimosa",
    "벨리니": "Bellini",
    "키르로얄": "Kir Royale",
    "화이트러시안": "White Russian",
    "블랙러시안": "Black Russian",
    "팔로마": "Paloma",
    "카이피리냐": "Caipirinha",
    "섹스온더비치": "Sex on the Beach",
    "프렌치75": "French 75",
    "다크앤스토미": "Dark 'N' Stormy",
    "아이리시커피": "Irish Coffee",
    "허리케인": "Hurricane",
    "좀비": "Zombie",
    "싱가포르슬링": "Singapore Sling",
    "그래스호퍼": "Grasshopper",
    "브랜디알렉산더": "Brandy Alexander",
    "롭로이": "Rob Roy",
    "갓파더": "Godfather",
    "갓마더": "Godmother",
    "러스티네일": "Rusty Nail",
    "브램블": "Bramble",
    "라스트워드": "Last Word",
    "클로버클럽": "Clover Club",
    "톰콜린스": "Tom Collins",
    "존콜린스": "John Collins",
    "씨브리즈": "Sea Breeze",
    "베이브리즈": "Bay Breeze",
    "퍼지네이블": "Fuzzy Navel",
    "카미카제": "Kamikaze",
    "비52": "B-52",
    "레몬드롭": "Lemon Drop Martini",
    "블루라군": "Blue Lagoon",
    "솔티독": "Salty Dog",
    "그레이하운드": "Greyhound",
    "플랜터스펀치": "Planters Punch",
    "럼펀치": "Rum Punch",
    "페인킬러": "Painkiller",
    "블루하와이안": "Blue Hawaiian",
    "머드슬라이드": "Mudslide",
    "화이트레이디": "White Lady",
    "하비웰뱅어": "Harvey Wallbanger",
    "스프리츠": "Aperol Spritz",
    "프렌치커넥션": "French Connection",
}

KOREAN_CATEGORY_MAP = {
    "무알콜": "Non alcoholic",
    "알코올": "Alcoholic",
}

# 카테고리 검색용 드롭다운
SPIRIT_CATEGORIES = [
    "보드카", "진", "럼", "화이트럼", "위스키", "버번", "테킬라", "브랜디", "샴페인", "와인",
]

INGREDIENT_CATEGORIES = [
    "레몬", "라임", "오렌지", "파인애플", "크랜베리", "콜라",
    "탄산수", "토닉워터", "우유", "커피", "민트", "설탕", "계란",
]


def api_get(endpoint: str, params: dict[str, str] | None = None) -> dict[str, Any]:
    url = f"{API_BASE}/{endpoint}"
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def normalize_keyword(keyword: str) -> str:
    cleaned = keyword.strip()
    return (
        KOREAN_INGREDIENT_MAP.get(cleaned)
        or KOREAN_COCKTAIL_NAME_MAP.get(cleaned)
        or KOREAN_CATEGORY_MAP.get(cleaned)
        or cleaned
    )


def extract_ingredients(drink: dict[str, Any]) -> list[dict[str, str]]:
    ingredients: list[dict[str, str]] = []

    for index in range(1, 16):
        ingredient = (drink.get(f"strIngredient{index}") or "").strip()
        measure = (drink.get(f"strMeasure{index}") or "").strip()

        if ingredient:
            ingredients.append({
                "name": ingredient,
                "measure": measure,
            })

    return ingredients


def format_drink(drink: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": drink.get("idDrink", ""),
        "name": drink.get("strDrink", ""),
        "category": drink.get("strCategory", ""),
        "alcoholic": drink.get("strAlcoholic", ""),
        "glass": drink.get("strGlass", ""),
        "instructions": drink.get("strInstructions", ""),
        "image": drink.get("strDrinkThumb", ""),
        "ingredients": extract_ingredients(drink),
    }


def search_by_name(keyword: str) -> list[dict[str, Any]]:
    data = api_get("search.php", {"s": keyword})
    drinks = data.get("drinks") or []
    return [format_drink(drink) for drink in drinks]


def collect_all_cocktails() -> list[dict[str, Any]]:
    cocktails: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for letter in string.ascii_lowercase:
        try:
            data = api_get("search.php", {"f": letter})
        except requests.RequestException:
            continue

        drinks = data.get("drinks") or []

        for drink in drinks:
            if not isinstance(drink, dict):
                continue

            drink_id = drink.get("idDrink")
            if drink_id and drink_id not in seen_ids:
                seen_ids.add(drink_id)
                cocktails.append(format_drink(drink))

    return cocktails


_all_cocktails_cache: list[dict[str, Any]] | None = None


def get_all_cocktails_cached() -> list[dict[str, Any]]:
    global _all_cocktails_cache
    if _all_cocktails_cache is None:
        _all_cocktails_cache = collect_all_cocktails()
    return _all_cocktails_cache


def search_by_ingredient(keyword: str) -> list[dict[str, Any]]:
    """
    TheCocktailDB 무료 테스트키는 filter.php?i= 결과를 1개로 제한해버려서
    (실제로 확인해보면 재료가 뭐든 1개만 옴), 이 API 대신 이미 받아둔 전체
    목록(get_all_cocktails_cached)에서 재료 이름이 일치하는 칵테일을 직접
    걸러낸다. 제한이 없는 search.php(f=글자) 기반이라 개수가 정확하다.
    """
    target = keyword.strip().lower()
    if not target:
        return []

    return [
        drink
        for drink in get_all_cocktails_cached()
        if any(target in ing["name"].lower() for ing in drink["ingredients"])
    ]


def search_non_alcoholic() -> list[dict[str, Any]]:
    """filter.php?a=Non_Alcoholic도 동일하게 1개로 제한되므로, 전체 목록에서
    직접 걸러낸다."""
    return [
        drink
        for drink in get_all_cocktails_cached()
        if drink["alcoholic"].strip().lower() == "non alcoholic"
    ]


def search_cocktails(keyword: str, mode: str) -> list[dict[str, Any]]:
    api_keyword = normalize_keyword(keyword)

    if not keyword.strip():
        return []

    if keyword.strip() == "무알콜":
        return search_non_alcoholic()

    if mode == "name":
        return search_by_name(api_keyword)

    if mode == "ingredient":
        return search_by_ingredient(api_keyword)

    name_results = search_by_name(api_keyword)
    ingredient_results = search_by_ingredient(api_keyword)

    merged: dict[str, dict[str, Any]] = {}
    for drink in name_results + ingredient_results:
        merged[drink["id"]] = drink

    return list(merged.values())


@app.route("/")
def index():
    keyword = request.args.get("keyword", "").strip()
    mode = request.args.get("mode", "all")

    cocktails: list[dict[str, Any]] = []
    all_cocktails: list[dict[str, Any]] = []
    error_message = ""

    if keyword:
        try:
            cocktails = search_cocktails(keyword, mode)
        except requests.RequestException:
            error_message = "칵테일 API 연결에 실패했습니다. 잠시 후 다시 시도해주세요."
        except (AttributeError, TypeError, KeyError, ValueError):
            # 등록되지 않은 단어를 검색했을 때 API가 예상과 다른 형태의 응답을 주는
            # 경우가 있다. 에러 화면 대신 "검색 결과 없음"으로 처리한다.
            cocktails = []
    else:
        try:
            all_cocktails = get_all_cocktails_cached()
        except requests.RequestException:
            error_message = "칵테일 API 연결에 실패했습니다. 잠시 후 다시 시도해주세요."

    return render_template(
        "index.html",
        keyword=keyword,
        mode=mode,
        cocktails=cocktails,
        all_cocktails=all_cocktails,
        error_message=error_message,
        spirit_categories=SPIRIT_CATEGORIES,
        ingredient_categories=INGREDIENT_CATEGORIES,
    )


@app.route("/download-csv")
def download_csv():
    keyword = request.args.get("keyword", "").strip()
    mode = request.args.get("mode", "all")

    try:
        cocktails = search_cocktails(keyword, mode) if keyword else collect_all_cocktails()
    except requests.RequestException:
        return Response(
            "API 연결에 실패했습니다.",
            status=502,
            mimetype="text/plain; charset=utf-8",
        )
    except (AttributeError, TypeError, KeyError, ValueError):
        cocktails = []

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "칵테일명",
        "카테고리",
        "알코올 여부",
        "사용 잔",
        "재료",
        "제조법",
        "이미지",
    ])

    for drink in cocktails:
        ingredient_text = ", ".join(
            f'{item["name"]} {item["measure"]}'.strip()
            for item in drink["ingredients"]
        )

        writer.writerow([
            drink["name"],
            drink["category"],
            drink["alcoholic"],
            drink["glass"],
            ingredient_text,
            drink["instructions"],
            drink["image"],
        ])

    csv_data = output.getvalue()
    output.close()

    filename = "cocktail_results.csv" if keyword else "all_cocktails.csv"

    return Response(
        "\ufeff" + csv_data,
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )


if __name__ == "__main__":
    app.run(debug=True)
