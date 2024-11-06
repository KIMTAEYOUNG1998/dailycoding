import csv
from playwright.sync_api import sync_playwright

def crawl_naver_blog(keyword, max_articles):
    results = []
    search_url = f"https://search.naver.com/search.naver?where=post&query={keyword}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(search_url)

        # 블로그 링크 목록을 가져오는 부분
        try:
            blog_links = page.locator("a.sh_blog_title")
            links = blog_links.evaluate_all("elements => elements.map(el => el.href)")[:max_articles]
        except Exception as e:
            print(f"Error finding blog links: {e}")
            return

        # 각 블로그 페이지를 열어서 제목과 콘텐츠를 추출
        for link in links:
            try:
                page.goto(link)
                page.wait_for_timeout(2000)  # 페이지 로드 대기
                title = page.locator("h3.se_textarea").inner_text()
                content = page.locator("div.se-main-container").inner_text()
                results.append({"title": title, "content": content})
            except Exception as e:
                print(f"Error on blog page {link}: {e}")
                continue  # 오류가 발생한 경우 다음 링크로 이동

    # 결과를 CSV 파일에 저장
    with open("naver_blog_results.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["title", "content"])
        writer.writeheader()
        writer.writerows(results)

    print("크롤링 완료 및 CSV 저장 완료!")

# 실행 예시
