# Basic example with Korean content

`cvgen` 스크립트를 사용하여 YAML 파일을 처리하고, 최종적으로 `rendercv`를 통해 다양한 형식의 이력서를 생성하는 워크플로우의 한 예시입니다.

⚠️ 제대로 된 LaTeX 한글 렌더링을 위해서는 `kotex`, `xelatex` 등 **LaTeX 한글 지원 패키지가 로컬 환경에 설치**되어 있어야 합니다.

## 프로세스 개요

```bash
make
```

위 명령어를 실행하면 프로세스의 동작을 간단히 확인해볼 수 있습니다.

이 프로세스는 다음 명령어를 실행합니다:

```bash
cvgen filter extended_template.yaml --target-verbosity 1 --include-tags '' \
| cvgen collapse -k ko > output_ko.yaml \
&& rendercv render output_ko.yaml --use-local-latex-command xelatex
```

이 명령어는 다음과 같은 단계로 실행됩니다:

1. `cvgen filter`: YAML 파일을 필터링합니다.
2. `cvgen collapse`: 다국어 내용에서 특정 언어로 된 내용만 추출합니다.
3. `rendercv render`: 최종 YAML을 다양한 형식으로 변환합니다.

## 단계별 설명

### 1. cvgen filter

```bash
cvgen filter extended_template.yaml --target-verbosity 1 --include-tags ''
```

- `extended_template.yaml`: 필터링할 YAML 파일입니다.
- `--target-verbosity 1`: 이 값 이하의 verbosity를 가진 내용만 남깁니다.
- `--include-tags ''`: 특정 태그를 포함하는 내용만 남기는 옵션인데, 이 예시에서는 모든 태그를 배제합니다.

예시:

```yaml
# 입력
projects:
  - name:
      en: "Project A"
      ko: "프로젝트 A"
    highlights:
      - content:  # 포함하며, content 키 안에 있는 내용만 남김
          en: "Description in English"
          ko: "한국어 설명"
        verbosity: 1.0
      - content:  # 태그가 달려 있어 배제
          en: "Additional detail"
          ko: "추가 세부사항"
        verbosity: 1.0
        tags: ["detail"]
      - content:  # verbosity가 너무 높아 배제
          en: "Additional detail"
          ko: "추가 세부사항"
        verbosity: 2.0

# 출력 (필터링 후)
projects:
  - name:
      en: "Project A"
      ko: "프로젝트 A"
    highlights:
      - en: "Description in English"  # 포함하며, content 키 안에 있는 내용만 남김
        ko: "한국어 설명"
```

### 2. cvgen collapse

```bash
cvgen collapse -k ko > output_ko.yaml
```

- `-k ko` 옵션은 한국어('ko') 버전의 내용을 선택합니다.
- 다국어로 작성된 내용에서 한국어로 작성된 내용만 추출합니다.
- 추출한 내용을 `output_ko.yaml` 파일에 (임시) 저장합니다.

예시:

```yaml
# 입력 (필터링 후)
projects:
  - name:
      en: "Project A"
      ko: "프로젝트 A"
    highlights:
      - en: "Description in English"
        ko: "한국어 설명"

# 출력 (축소 후)
projects:
  - name: "프로젝트 A"
    highlights:
      - "한국어 설명"
```

### 3. rendercv render

```
rendercv render output_ko.yaml --use-local-latex-command xelatex
```

- 앞에서 임시 저장한 `output_ko.yaml` 파일을 입력으로 사용합니다.
- LaTeX 렌더링에는 미리 로컬 환경에 준비한 `xelatex` 명령어를 사용합니다. (한글 지원을 위해 필수!)
- PDF, TeX, PNG 등 다양한 형식의 출력 파일을 생성합니다.

## 정리

이 프로세스를 통해, **다국어로 작성된 YAML 템플릿으로부터 특정 언어(이 경우 한국어)의 이력서를 쉽게 생성**할 수 있습니다. `cvgen` 스크립트는 내용을 필터링하고 일부 값을 추출하는 작업을 수행하며, `rendercv`는 최종적으로 다양한 형식의 문서를 생성합니다.

예시로 제시된 명령어에서 조금씩 수정해가며 실행해보시면, `cvgen`과 `rendercv`의 다양한 기능을 더욱 잘 이해하실 수 있을 것입니다.

### 참고 링크

- [rendercv CLI docs](https://docs.rendercv.com/user_guide/cli/)
- [kotex 관련 문서 - KTUG (한글 TeX 사용자 그룹)](http://wiki.ktug.org/wiki/wiki.php/ko.TeX)
