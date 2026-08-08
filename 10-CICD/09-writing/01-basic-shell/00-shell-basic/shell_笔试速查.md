# 掌握Shell脚本：从入门到精通

> 来源：https://blog.csdn.net/2502_93300404/article/details/161364802

## 引言

在前面的文章中，我们已经学习了 Linux 环境下的各种开发工具。Shell 脚本是连接这些工具的"胶水"——它能将系统命令、条件判断、循环和函数组合起来，实现自动化任务。

Shell 脚本属于解释型语言，无需编译，由解释器（如 bash）逐行解释执行。这使得它在系统管理、持续集成、日志分析等场景中不可替代。

## 第一部分：基础语法

### 一、脚本的基本结构

```bash
#!/bin/bash   # 首行必须声明解释器（shebang）
#             # 开头的行为注释

echo "Hello World"
```

执行方式：

```bash
# 方式1：显式调用解释器
bash myscript.sh

# 方式2：授权后直接执行
chmod u+x myscript.sh
./myscript.sh
```

### 二、变量

#### 1. 变量定义与取值

```bash
# 定义（等号两边不能有空格！）
a=100
str="hello world"
str2='single quote'

# 取值（必须用 $ 前缀）
echo $a          # 100
echo "$str"      # hello world

# 变量间赋值
s=$a
echo $s          # 100
```

#### 2. 单引号 vs 双引号

| 引号类型 | 特点 | 示例 |
| --- | --- | --- |
| 双引号 `""` | 允许变量替换 | `echo "$a"` → `100` |
| 单引号 `''` | 强引用，原样输出 | `echo '$a'` → `$a` |
| 无引号 | 仅适用于无空格字符串 | `a=100` |

```bash
name="world"
echo "hello $name"    # hello world（双引号解析变量）
echo 'hello $name'    # hello $name（单引号不解析）
```

#### 3. 从键盘读取

```bash
read -p "请输入你的名字：" name
echo "你好，$name"
```

#### 4. 变量分类

（原文此处仅有标题，无正文内容）

## 第二部分：条件判断

### 一、test 命令与中括号

条件判断有两种等效写法：

```bash
test $a = 1          # test 命令
[ $a = 1 ]           # 中括号（注意空格！）
```

空格规则非常重要：

```bash
# ✅ 正确
[ $a = 1 ]

# ❌ 错误（缺空格会导致语法错误）
[$a=1]
```

### 二、三种测试类型

| 测试类型 | 运算符 | 说明 | 示例 |
| --- | --- | --- | --- |
| 字符串 | `=`、`!=`、`-z`、`-n` | 判等/判空 | `[ "$str" = "abc" ]` |
| 数值 | `-eq`、`-ne`、`-gt`、`-ge`、`-lt`、`-le` | 等于/不等/大于/大于等于/小于/小于等于 | `[ $n -gt 100 ]` |
| 文件 | `-f`、`-d`、`-x`、`-r`、`-e` | 普通文件/目录/可执行/可读/存在 | `[ -f "/path" ]` |

注意：数值比较不能用 `>` 和 `<`，必须用 `-gt`、`-lt` 等。

### 三、if 语句

```bash
# 单分支
if [ "$input" = "ABC" ]; then
    echo "相等"
fi

# 双分支
if [ $num -gt 100 ]; then
    echo "大于100"
else
    echo "小于等于100"
fi

# 多分支
if [ -d "$file" ]; then
    echo "$file 是目录"
elif [ -f "$file" ]; then
    echo "$file 是普通文件"
else
    echo "$file 不存在"
fi
```

语法要点：

- `if` 和 `then` 在同一行时用 `;` 分隔
- 必须以 `fi` 结束

### 四、逻辑与和逻辑或

```bash
# 逻辑与：两个条件都满足
[ $n -ge 0 ] && [ $n -le 100 ]

# 逻辑或：两个条件满足其一
[ $n -lt 0 ] || [ $n -gt 100 ]
```

## 第三部分：循环结构

### 一、while 循环

```bash
# 密码验证（3次机会）
i=1
while [ $i -le 3 ]; do
    read -p "请输入密码：" input
    if [ "$input" = "123" ]; then
        echo "密码正确"
        break
    fi
    let i+=1
done

if [ $i -gt 3 ]; then
    echo "次数超限，退出"
    exit 1
fi
```

`let` 命令用于算术运算：`let i+=1` 等价于 `i=$((i+1))`。

### 二、for 循环

```bash
# 遍历列表
for item in apple banana orange; do
    echo $item
done

# 遍历数值范围
for i in {1..5}; do
    echo $i
done
```

### 三、循环对比

| 循环类型 | 执行条件 | 语法 |
| --- | --- | --- |
| `while` | 条件为真时执行 | `while [ condition ]; do ... done` |
| `until` | 条件为假时执行 | `until [ condition ]; do ... done` |
| `for` | 遍历列表 | `for var in list; do ... done` |

---

## 第四部分：case 语句

```bash
read -p "输入 yes 或 no：" input

case $input in
    yes|y|Y|YES)
        echo "你选择了是"
        ;;
    no|n|N|NO)
        echo "你选择了否"
        ;;
    *)
        echo "输入无效"
        ;;
esac
```

语法要点：

- 以 `case` 开头，`esac` 结尾
- 每个分支以 `)` 分隔
- 每个分支结束用 `;;`（双分号）
- `*` 匹配所有其他情况
- `|` 表示"或"（如 `yes|y|Y`）

---

## 第五部分：函数

### 一、函数定义与调用

```bash
# 函数定义（建议放在脚本最前面）
fun() {
    echo "这是一个函数"
}

# 函数调用
fun
```

### 二、函数传参

```bash
my_add() {
    echo "参数个数：$#"
    echo "第一个参数：$1"
    echo "第二个参数：$2"
    return $(($1 + $2))
}

# 传参调用
my_add 3 5
echo "返回值：$?"  # 8（$? 获取上一条命令的返回值）
```

函数参数和脚本参数是独立的：

- 在函数内，`$1` 是函数的参数
- 在函数外，`$1` 是脚本的参数

### 三、函数内的变量作用域

```bash
my_func() {
    local local_var="只在函数内有效"   # 局部变量
    global_var="整个脚本都能用"        # 全局变量
}

my_func
echo $local_var    # 空（函数外不可见）
echo $global_var   # 整个脚本都能用
```

| 关键字 | 作用域 |
| --- | --- |
| 默认（无修饰） | 全局，脚本任意位置可访问 |
| `local` | 仅函数内有效 |
| `unset` | 删除变量 |

---

## 第六部分：脚本互调

### 一、直接调用（独立进程）

```bash
# a.sh
echo "A 脚本 PID：$$"
./b.sh          # 启动新解释器执行 b.sh
```

`./b.sh` 会启动一个新的 bash 进程，两个脚本的 `$$`（进程 PID）不同。

### 二、点命令调用（同一解释器）

```bash
# a.sh
echo "A 脚本 PID：$$"
. ./b.sh        # 或 source ./b.sh
```

### 三、调用方式对比

| 调用方式 | 解释器 | 变量共享 | 适用场景 |
| --- | --- | --- | --- |
| `./b.sh` | 新进程 | ❌ 不共享 | 独立任务 |
| `. ./b.sh` 或 `source` | 同一进程 | ✅ 共享 | 共享变量、配置 |
| `./b.sh $var` | 新进程 | 通过参数传递 | 传特定数据 |

### 四、传参与环境变量

```bash
# a.sh
mySTR="hello"
./b.sh $mySTR          # 通过参数传递

# b.sh
echo $1                # 输出 hello
```

```bash
# 环境变量方式
export mySTR="hello"   # 将变量升级为环境变量
./b.sh                 # 子进程自动继承环境变量
echo $mySTR            # b.sh 中可以直接使用
```

### 五、C 语言调用 Shell 脚本

```c
#include <stdio.h>
#include <unistd.h>

int main() {
    printf("C 程序 PID：%d\n", getpid());
    
    // execl 替换当前进程为脚本解释器
    execl("./b.sh", "b.sh", NULL);
    
    // 以下代码不会执行（进程已被替换）
    return 0;
}
```

反向调用（Shell 调 C 程序）更简单——直接在脚本中写可执行文件路径即可，和调用 `ls`、`grep` 等系统命令完全一样。

---

## 第七部分：完整示例

```bash
#!/bin/bash
# 学生成绩管理系统

# 函数定义
check_grade() {
    local score=$1
    if [ $score -ge 90 ]; then
        echo "优秀"
    elif [ $score -ge 80 ]; then
        echo "良好"
    elif [ $score -ge 60 ]; then
        echo "及格"
    else
        echo "不及格"
    fi
}

# 主逻辑
echo "===== 学生成绩管理系统 ====="

while true; do
    read -p "请输入分数（输入-1退出）：" score
    
    # 输入验证
    if [ "$score" = "-1" ]; then
        echo "退出系统"
        break
    fi
    
    # 数值范围检查
    if [ $score -lt 0 ] || [ $score -gt 100 ]; then
        echo "分数必须在 0~100 之间"
        continue
    fi
    
    # 调用函数判定等级
    grade=$(check_grade $score)
    echo "成绩等级：$grade"
done
```

## 总结

### 一、核心语法速查

| 语法 | 写法 |
| --- | --- |
| 变量定义 | `a=100`（等号不能有空格） |
| 变量取值 | `$a` 或 `${a}` |
| if 语句 | `if [ 条件 ]; then ... fi` |
| while 循环 | `while [ 条件 ]; do ... done` |
| for 循环 | `for var in list; do ... done` |
| case 语句 | `case $var in 值) ... ;; esac` |
| 函数 | `func() { ... }` |
| 调用脚本 | `./b.sh`（独立进程）或 `. ./b.sh`（同一进程） |

### 二、常见错误

| 错误 | 正确写法 |
| --- | --- |
| `[$a=1]` | `[ $a = 1 ]`（空格！） |
| `a = 100` | `a=100`（等号不能有空格） |
| `if [$a=1] then` | `if [ $a = 1 ]; then` |
| `$1` 不解析 | 用双引号 `"$1"` |

### 三、一句话记忆

Shell 脚本通过变量存储数据、`if/while/case` 控制流程、函数封装逻辑、`./b.sh`（独立进程）或 `. ./b.sh`（同一进程）调用其他脚本，是连接 Linux 系统命令的自动化工具。
