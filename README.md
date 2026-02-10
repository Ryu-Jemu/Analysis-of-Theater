# Analysis-of-Theater

극장/지하철역/POI 및 영화 지표 분석 결과를 **단일 파일 대시보드**로 생성하는 프로젝트입니다.

- 실행: `./run.sh`
- 최종 결과물: `outputs/dashboard.html` (단일 파일)

## 최근 결과물 (업로드용)
- 대시보드 파일: [`outputs/dashboard.html`](outputs/dashboard.html)
- 마지막 생성 일시: `2026-02-11 03:52:39 KST`
- 마지막 문서 업데이트: `2026-02-11 04:03:51 KST`

GitHub README에서는 HTML iframe을 직접 렌더링하지 않으므로, 위 링크로 대시보드를 열어 결과를 확인합니다.

## 실행 방법
```bash
pip install -r requirements.txt
chmod +x run.sh
./run.sh
```

## 출력 정책 (단일 대시보드 모드)
- 파이프라인 실행 중 PNG/HTML/CSV 중간 산출물이 잠시 생성될 수 있습니다.
- `pipeline.py`가 `outputs/dashboard.html`에 시각화/지도/CSV 미리보기를 **인라인 임베드**합니다.
- 대시보드 생성 후 중간 산출물은 자동 삭제됩니다.
- 따라서 실행 완료 후 `outputs/`에는 `dashboard.html`만 남습니다(및 `.gitkeep`가 있으면 유지).

## 포함되는 시각화
- 영화 지표: 개봉편수/관객수/매출 이미지
- 지도: 극장+역 지도, 극장+쇼핑몰 지도(iframe srcdoc)
- 기타: 3D 분석, 소비지출-점유율 상관, 워드클라우드
- 키워드 CSV: 상위 10행 미리보기

## 설정
- 경로/실행 단계는 `config.yaml`에서 제어합니다.
- API 키는 `.env` 사용:
```bash
cp .env.example .env
```

필수(선택 단계 실행 시):
```dotenv
KAKAO_REST_API_KEY=...
NAVER_CLIENT_ID=...
NAVER_CLIENT_SECRET=...
```
