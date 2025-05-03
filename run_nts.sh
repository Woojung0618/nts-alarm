#!/bin/bash

# conda 초기화 (conda 경로에 따라 수정 필요할 수도 있음)
source ~/miniconda3/etc/profile.d/conda.sh

# 가상환경 활성화
conda activate test02

# 크롤링 스크립트 실행
python /Users/woojung/Projects/nts_alarm/nts_crawling.py

