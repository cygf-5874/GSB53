#!/usr/bin/env python3
"""固定验收入口：fmtnum 的「对外保证」。**别改这个文件。**

用法：
  python3 check.py                跑全部场景，全过才退 0
  python3 check.py -list          列出全部场景
  python3 check.py --only mode    只跑一组（mode / carry / precision / grouping）
  python3 check.py --only mode,carry

四组共 9 个场景：
  mode      3 —— HALF_UP 边界 / HALF_EVEN 边界 / DOWN 与 UP 对照（含负数零）
  carry     2 —— 9.999 溢出到整数位 / 小数位内部连续进位
  precision 2 —— Decimal 无损 / 10^30 量级不丢精度
  grouping  2 —— 默认 3 位分组 / 印度式分组

只依赖标准库；判据完全确定，不读时间、不用随机源。失败不早退。
"""

import sys
from decimal import Decimal

from fmtnum import format_fixed


class CheckFailure(Exception):
    def __init__(self, message, expected="-", actual="-"):
        super().__init__(message)
        self.expected = expected
        self.actual = actual


def eq(got, want, what):
    if got != want:
        raise CheckFailure(what, repr(want), repr(got))


def fmt(value, digits, mode, grouping=None):
    return format_fixed(value, digits, mode, grouping)


# ---------------------------------------------------------------------------
# [mode] 3
# ---------------------------------------------------------------------------

def mode_half_up():
    eq(fmt(Decimal("1.005"), 2, "HALF_UP"), "1.01", "Decimal 1.005 保留 2 位 HALF_UP")
    eq(fmt(1.005, 2, "HALF_UP"), "1.01", "1.005 保留 2 位 HALF_UP")
    eq(fmt(2.675, 2, "HALF_UP"), "2.68", "2.675 保留 2 位 HALF_UP")
    eq(fmt(0.125, 2, "HALF_UP"), "0.13", "0.125 保留 2 位 HALF_UP")
    eq(fmt("1.005", 2, "HALF_UP"), "1.01", '字符串 "1.005" 保留 2 位 HALF_UP')


def mode_half_even():
    eq(fmt(0.125, 2, "HALF_EVEN"), "0.12", "0.125 保留 2 位 HALF_EVEN（向偶数）")
    eq(fmt(0.625, 2, "HALF_EVEN"), "0.62", "0.625 保留 2 位 HALF_EVEN（向偶数）")
    eq(fmt(2.5, 0, "HALF_EVEN"), "2", "2.5 保留 0 位 HALF_EVEN（向偶数）")
    eq(fmt(-0.5, 0, "HALF_EVEN"), "-0", "-0.5 保留 0 位 HALF_EVEN（向偶数，保留负零）")
    eq(fmt(Decimal("0.375"), 2, "HALF_EVEN"), "0.38", "Decimal 0.375 保留 2 位 HALF_EVEN")


def mode_down_up():
    eq(fmt(1.29, 1, "DOWN"), "1.2", "1.29 向零舍入")
    eq(fmt(1.21, 1, "UP"), "1.3", "1.21 背离零舍入")
    eq(fmt(-1.29, 1, "DOWN"), "-1.2", "-1.29 向零舍入")
    eq(fmt(-1.21, 1, "UP"), "-1.3", "-1.21 背离零舍入")
    eq(fmt(-0.001, 2, "DOWN"), "-0.00", "负数零：-0.001 向零舍入保留符号")
    eq(fmt(-0.001, 2, "UP"), "-0.01", "-0.001 背离零舍入")


# ---------------------------------------------------------------------------
# [carry] 2
# ---------------------------------------------------------------------------

def carry_rollover():
    eq(fmt(9.999, 2, "HALF_UP"), "10.00", "9.999 保留 2 位 HALF_UP（进位溢出到整数位）")
    eq(fmt(0.999, 2, "HALF_UP"), "1.00", "0.999 保留 2 位 HALF_UP（进位溢出到整数位）")
    eq(fmt(Decimal("9.995"), 2, "HALF_UP"), "10.00", "Decimal 9.995 保留 2 位 HALF_UP")
    eq(fmt(Decimal("99.999"), 2, "HALF_UP"), "100.00", "Decimal 99.999 保留 2 位 HALF_UP")


def carry_multi():
    eq(fmt(0.099, 2, "HALF_UP"), "0.10", "0.099 保留 2 位 HALF_UP（小数位内部进位）")
    eq(fmt(1.0999, 2, "HALF_UP"), "1.10", "1.0999 保留 2 位 HALF_UP（小数位内部进位）")
    eq(fmt(12.099, 2, "HALF_UP"), "12.10", "12.099 保留 2 位 HALF_UP（小数位内部进位）")
    eq(fmt(Decimal("3.9499"), 2, "HALF_UP"), "3.95", "Decimal 3.9499 保留 2 位 HALF_UP")


# ---------------------------------------------------------------------------
# [precision] 2
# ---------------------------------------------------------------------------

def precision_decimal_exact():
    eq(fmt(Decimal("2.675"), 2, "HALF_UP"), "2.68", "Decimal 2.675 无损")
    eq(fmt(Decimal("9007199254740993.00"), 2, "HALF_UP"), "9007199254740993.00",
       "超过 float 精度的 Decimal 必须无损")
    eq(fmt(Decimal("0.10"), 1, "HALF_UP"), "0.1", "Decimal 0.10 保留 1 位")
    eq(fmt(Decimal("123456789.987654321"), 6, "HALF_EVEN"), "123456789.987654",
       "高精度 Decimal 保留 6 位")


def precision_huge():
    eq(fmt(10 ** 30, 0, "HALF_UP"), "1" + "0" * 30, "10^30（int）保留 0 位")
    eq(fmt(Decimal("1e30"), 2, "HALF_UP"), "1" + "0" * 30 + ".00", "10^30（Decimal）保留 2 位")
    eq(fmt(Decimal("1000000000000000000000000000001"), 0, "HALF_UP"),
       "1000000000000000000000000000001", "10^30+1 不得丢精度")
    eq(fmt(10 ** 30 + 1, 0, "DOWN"), "1000000000000000000000000000001", "10^30+1（int）向零舍入")


# ---------------------------------------------------------------------------
# [grouping] 2
# ---------------------------------------------------------------------------

def grouping_thousand():
    eq(fmt(Decimal("1234567.891"), 2, "HALF_UP", "thousand"), "1,234,567.89",
       "千分位分组（默认 3 位）带小数")
    eq(fmt(1234567, 0, "HALF_UP", "thousand"), "1,234,567", "千分位分组（默认 3 位）整数")
    eq(fmt(Decimal("1234.5"), 1, "HALF_UP", "thousand"), "1,234.5", "千分位分组 4 位整数")
    eq(fmt(-1234567, 0, "DOWN", "thousand"), "-1,234,567", "千分位分组负数")


def grouping_indian():
    eq(fmt(123456789012, 0, "HALF_UP", "indian"), "1,23,45,67,89,012",
       "印度式分组（首段 3 位、其后每段 2 位）")
    eq(fmt(1234567, 0, "HALF_UP", "indian"), "12,34,567", "印度式分组 7 位")
    eq(fmt(12345, 0, "HALF_UP", "indian"), "12,345", "印度式分组 5 位")
    eq(fmt(1234, 0, "HALF_UP", "indian"), "1,234", "印度式分组 4 位")


GROUPS = [
    ("mode", [
        ("half_up", "HALF_UP 在 0.5 位与 1.005 上的结果", mode_half_up),
        ("half_even", "HALF_EVEN 在 0.5 位上的结果", mode_half_even),
        ("down_up", "DOWN / UP 对照，含负数零", mode_down_up),
    ]),
    ("carry", [
        ("rollover", "进位溢出到整数位（9.999）", carry_rollover),
        ("multi", "小数位内部连续进位", carry_multi),
    ]),
    ("precision", [
        ("decimal_exact", "Decimal 输入无损", precision_decimal_exact),
        ("huge", "10^30 量级不丢精度", precision_huge),
    ]),
    ("grouping", [
        ("thousand", "默认 3 位分组", grouping_thousand),
        ("indian", "印度式分组（首段 3 位、其后每段 2 位）", grouping_indian),
    ]),
]


def parse_argv(argv):
    do_list = False
    only = None
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("-list", "--list"):
            do_list = True
        elif arg in ("--only", "--group"):
            i += 1
            if i >= len(argv):
                sys.stderr.write("--only 需要一个组名（mode/carry/precision/grouping）\n")
                raise SystemExit(2)
            only = {p.strip() for p in argv[i].split(",") if p.strip()}
        elif arg in ("-h", "--help"):
            sys.stdout.write("用法: python3 check.py [-list] [--only <组名>]\n")
            raise SystemExit(0)
        else:
            sys.stderr.write("未知参数: %s\n" % arg)
            raise SystemExit(2)
        i += 1
    return do_list, only


def main(argv):
    do_list, only = parse_argv(argv)

    if do_list:
        for group, scenarios in GROUPS:
            for name, why, _fn in scenarios:
                sys.stdout.write("[%-9s] %-14s %s\n" % (group, name, why))
        return 0

    selected = []
    for group, scenarios in GROUPS:
        if only is not None and group not in only:
            continue
        for name, why, fn in scenarios:
            selected.append((group, name, why, fn))

    if not selected:
        sys.stderr.write("没有匹配的场景\n")
        return 2

    passed = 0
    failed = 0
    for group, name, _why, fn in selected:
        try:
            fn()
        except CheckFailure as exc:
            failed += 1
            sys.stdout.write("FAIL %s/%s  期望=%s 实际=%s（%s）\n"
                             % (group, name, exc.expected, exc.actual, exc))
            continue
        except Exception as exc:  # noqa: BLE001
            failed += 1
            sys.stdout.write("FAIL %s/%s  期望=正常返回 实际=%s: %s\n"
                             % (group, name, type(exc).__name__, exc))
            continue
        passed += 1
        sys.stdout.write("PASS %s/%s\n" % (group, name))

    total = len(selected)
    sys.stdout.write("结果：通过 %d/%d\n" % (passed, total))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
