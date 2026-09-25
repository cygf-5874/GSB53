# fmtnum —— 定点数字格式化

把数字格式化成**固定小数位**的字符串：可指定小数位数、舍入模式，可选千分位分组。
用于账目、报表这类「显示出来的结果必须和十进制手算完全对得上」的场景。

`fmtnum/` 下是完整实现，`tests/` 是既有用例，`check.py` 是固定验收入口，`repro.py` 是
调用方给的复现脚本。零第三方依赖，`decimal` 是标准库，Python 3.9 以上直接跑。

```python
from fmtnum import format_fixed

format_fixed(1.005, 2, "HALF_UP")                 # '1.01'
format_fixed("9.999", 2, "HALF_UP")               # '10.00'
format_fixed(-0.001, 2, "DOWN")                   # '-0.00'
format_fixed(1234567, 0, "HALF_UP", "thousand")   # '1,234,567'
```

## 接口

```
format_fixed(value, digits, mode, grouping=None) -> str
```

| 参数 | 取值 | 说明 |
| --- | --- | --- |
| `value` | `str` / `float` / `int` / `Decimal` | 待格式化的数 |
| `digits` | `int`，`>= 0` | 小数点后保留的位数 |
| `mode` | `"HALF_UP"` / `"HALF_EVEN"` / `"DOWN"` / `"UP"` | 舍入模式 |
| `grouping` | `None` / `"thousand"` / `"indian"` | 千分位分组方式 |

入参不合法（`digits` 为负、`mode` 或 `grouping` 不认识、`value` 无法解析）时抛
`FmtNumError`（`ValueError` 的子类）。函数签名与异常类型属于对外契约，不要改。

## 对外保证（8 条）

下面每一条都是对外保证。**验收以 `check.py` 为准**，语义细节以本节为准。

1. **十进制定点舍入**：`format_fixed` 一律按**十进制**判定并舍入，不许走二进制浮点的
   `round()`。输出固定带 `digits` 位小数（`digits` 为 `0` 时没有小数点）。
2. **四种模式**：`HALF_UP` / `HALF_EVEN` / `DOWN` / `UP` 的语义以下面的**算例表**为准
   （含 `0.5` 位、`1.005`、`-0.5` 这些边界）。
3. **`Decimal` 无损**：`Decimal` 输入必须按它的十进制值**无损**使用，不许先转 `float`。
   超过 `float` 精度的 `Decimal`（如 `9007199254740993.00`）也必须逐位正确。
4. **进位传播**：舍入进位必须能一路传播出去 —— `9.999` 保留 2 位在 `HALF_UP` 下是
   `10.00`，`0.999` 保留 2 位是 `1.00`。
5. **分组方式**：`grouping=None` 不加分隔符；`grouping="thousand"` 每 3 位一组；
   `grouping="indian"` 时**首段 3 位、其后每段 2 位**（如 `1234567` → `12,34,567`）。
   分组只作用于整数部分，符号与小数点照常。
6. **负数零**：舍入后数值为零时仍保留输入符号 —— `DOWN` 模式下的 `-0.001` 输出 `-0.00`。
7. **超大整数不丢精度**：`10^30` 量级（含末位的 ±1）必须逐位正确，不得因浮点而丢位。
8. **`nan` / `inf`**：`nan` 返回 `"NaN"`；`inf` 返回 `"Infinity"`，`-inf` 返回 `"-Infinity"`；
   都不抛异常。

### 入参的十进制语义

- `str` / `int` / `Decimal`：按**十进制字面值**使用，绝不经过二进制浮点。
- `float`：按其**最短往返十进制表示**（即 `str(value)`）使用。于是同一个字面量，
  写成 `1.005`、`"1.005"` 还是 `Decimal("1.005")`，格式化结果必须一致。

### 算例表（模式语义的唯一出处）

`value` 一列写的是十进制字面值（`float` / `str` / `Decimal` 三种入参等价）。

| value | digits | HALF_UP | HALF_EVEN | DOWN | UP |
| --- | --- | --- | --- | --- | --- |
| `0.125` | 2 | `0.13` | `0.12` | `0.12` | `0.13` |
| `1.005` | 2 | `1.01` | `1.00` | `1.00` | `1.01` |
| `2.5` | 0 | `3` | `2` | `2` | `3` |
| `-0.5` | 0 | `-1` | `-0` | `-0` | `-1` |
| `9.999` | 2 | `10.00` | `10.00` | `9.99` | `10.00` |
| `-0.001` | 2 | `-0.00` | `-0.00` | `-0.00` | `-0.01` |

补一句口径，避免歧义：`DOWN` 是**向零**舍入，`UP` 是**背离零**舍入；`HALF_UP` 是
「恰好在半位时背离零」，`HALF_EVEN` 是「恰好在半位时取偶」（也就是所谓银行家舍入）。

## 目录

```
fmtnum/
  __init__.py   对外导出
  rounding.py   舍入模式与定点舍入
  grouping.py   千分位分组
  format.py     format_fixed
tests/          既有用例
check.py        固定验收入口（**勿改**）
repro.py        调用方给的复现脚本（**勿改**）
scripts/check.sh
```

## 怎么跑

```bash
python3 -m unittest discover -s tests      # 既有用例
python3 check.py                           # 全部验收场景，全过才退 0
python3 check.py -list                     # 列出全部场景
python3 check.py --only mode               # 只跑一组（mode / carry / precision / grouping）
python3 check.py --only mode,carry
python3 repro.py                           # 调用方给的复现
```

`check.py` 是**固定验收入口，不要改它**；失败不早退，一次把问题全暴露出来。

## 版本前提

- Python 3.9 及以上，只用标准库（`decimal` / `unittest`），不需要联网、数据库或中间件。
- 判据完全确定：输入写死，不依赖时间、随机源或机器速度。
