# 2. Jenkinsfile（声明式）

## 核心认识

- **Jenkinsfile** 放在仓库里 → 同样是「代码即流水线」  
- **声明式（Declarative）** Pipeline 最常见，面试够用  
- 思想与 `.gitlab-ci.yml` 一致：阶段、步骤、条件、制品  

## 极简对照

| 概念 | GitLab CI | Jenkins |
|------|-----------|---------|
| 配置文件 | `.gitlab-ci.yml` | `Jenkinsfile` |
| 阶段 | `stages` / `stage:` | `stages { stage('test') { ... } }` |
| 命令 | `script:` | `steps { sh 'pytest ...' }` |
| 触发 | `rules` / 项目集成 | Webhook / 定时 / 多分支流水线 |
| 工人 | Runner | Agent |

```groovy
// 概念示意，不必背语法细节
pipeline {
  agent any
  stages {
    stage('test') {
      steps {
        sh 'pytest tests/smoke -m smoke'
      }
    }
  }
}
```

口述：

> 「Jenkinsfile 声明式写 stage 和 steps，和 GitLab 的 stages/script 是同一层抽象；我会看文档补语法，迁移成本主要在触发与凭证集成。」
