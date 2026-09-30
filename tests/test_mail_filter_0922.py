#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证 scan_job_mail 的过滤修复：广告邮件要拦，真招聘要放行。"""
import sys

sys.path.insert(0, "scripts")
from scan_job_mail import is_job_mail  # noqa: E402

CASES = [
    # (说明, 期望是否是招聘邮件, subject, sender, body)
    ("51job 营销·AI证书培训卖课(全角AD)",
     False,
     "王小满，你在前司的经验很不错！被邀请参加AI证书培训，可领政府补贴￥5850（AD）",
     "前程无忧(51Job) <51job-mkt@recruitment.51job.test>",
     "亲爱的王小满：AI正在重塑各行各业。开设两门AI证书线下培训。企微添加老师，领取补贴资格→ 关注微信公众号。"),

    ("51job 营销·职位动态推送(无AD标记)",
     False,
     "@王先生，非常欣赏您某高校的工商管理学习经历，与我们热招的行政/后勤职位要求高度一致",
     "前程无忧 <service@quickjobs.51job.test>",
     "亲爱的王先生：您有一条职位动态未读。邀您投递简历，职位急招中！立即查看。关注微信公众号。如果您不想再收到此类邮件，请点击退订。"),

    ("TÜV莱茵 申请确认（真招聘，必须放行）",
     True,
     "Thank you for applying to TUV Rheinland(Shanghai) Co., Ltd.",
     '"TÜV Rheinland@myHR" <system@successfactors.test>',
     "Dear 先生 王, Thank you for your interest in TÜV Rheinland as AI与智能产品交互测评工程师. Allow us to review your profile."),

    ("国芯微 感谢应聘通知（真招聘，必须放行）",
     True,
     "感谢应聘通知",
     "杭州国芯微电子股份有限公司 <HR@shmail.ibeisen.test>",
     "亲爱的 王先生：感谢投递我司的 DFT设计工程师 岗位，很抱歉告知您，目前您的简历不完全匹配招聘要求。"),

    ("九联科技 求职反馈（真招聘，必须放行）",
     True,
     "九联科技求职反馈 | 致[王小满]同学",
     '"广东九联科技股份有限公司-人力资源部" <hr@unionman.test>',
     "王小满 同学：感谢您应聘广东九联科技股份有限公司。经综合评估，暂不匹配岗位要求。"),
]

fail = 0
for desc, want, subj, sender, body in CASES:
    got, why = is_job_mail(subj, sender, body)
    ok = (got == want)
    if not ok:
        fail += 1
    mark = "✅" if ok else "❌ 不符"
    print(f"{mark} | 期望={'招聘' if want else '广告'} 实际={'招聘' if got else '广告'}"
          f" | {desc} | 命中规则={why}")

print()
print(f"结果：{len(CASES)-fail}/{len(CASES)} 通过")
if __name__ == "__main__":
    sys.exit(1 if fail else 0)
