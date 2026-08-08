# Demo 02｜用例与发现规则

对应文档：[02-用例与发现规则.md](../../02-用例与发现规则.md)

## 运行

```bash
cd demos/02-discovery

# 应收集到：test_demo02_ok.py + demo02_fixture_test.py
# 不应收集：helpers_not_collected.py
pytest -v

# 只跑名字里带 login 的
pytest -k login -v

# 只跑某一个
pytest test_demo02_ok.py::TestUser::test_create -v
```

## 你要观察到什么

1. `helpers_not_collected.py` 里的 `assert False` **没有**把套件弄红 → 没被收集  
2. `-k login` 只跑 `test_login_*`  
3. `TestUser` 类里的方法会被跑  
4. fixture `client` 自动注入到 `test_api`  
