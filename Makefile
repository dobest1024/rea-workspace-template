.PHONY: help doctor verify stage test

help:
	@echo 'doctor: REA MCP 自检 | verify: 原件校验 | stage: 创建分析副本 | test: 脚本测试'
	@echo '新目标: python3 scripts/workspace.py new /absolute/path/to/project'
	@echo '导入:   python3 scripts/workspace.py import /absolute/path/to/sample'

doctor:
	rea --version
	rea mcp doctor --json

verify:
	python3 scripts/workspace.py verify

stage:
	python3 scripts/workspace.py stage

test:
	python3 -m unittest discover -s tests -v
