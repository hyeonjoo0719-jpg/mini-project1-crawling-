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
    "진": "Gin",
    "럼": "Rum",
    "화이트럼": "White rum",
    "위스키": "Whiskey",
    "버번": "Bourbon",
    "테킬라": "Tequila",
    "브랜디": "Brandy",
    "샴페인": "Champagne",
    "와인": "Wine",
    "레몬": "Lemon",
    "라임": "Lime",
    "오렌지": "Orange",
    "파인애플": "Pineapple juice",
    "크랜베리": "Cranberry juice",
    "콜라": "Coca-Cola",
    "탄산수": "Soda water",
    "토닉워터": "Tonic water",
    "우유": "Milk",
    "커피": "Coffee",
    "민트": "Mint",
    "설탕": "Sugar",
    "계란": "Egg",
}

KOREAN_CATEGORY_MAP = {
    "무알콜": "Non alcoholic",
    "알코올": "Alcoholic",
}

# 카테고리 검색용 드롭다운 목록 (주종 / 재료 두 가지)
# KOREAN_INGREDIENT_MAP에 이미 등록된 한글 표현들을 두 그룹으로 나눠서 재사용한다.
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
    return KOREAN_INGREDIENT_MAP.get(cleaned, KOREAN_CATEGORY_MAP.get(cleaned, cleaned))


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


# 첫 화면과 재료검색 모두 이 전체 목록을 기반으로 동작한다. A~Z를 전부 훑어야
# 해서(26번 API 호출) 매번 새로 불러오면 느리므로, 서버가 켜져있는 동안은 한 번
# 불러온 결과를 재사용한다.
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
