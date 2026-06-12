# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import importlib.util
import os
import re
from html import escape, unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zipfile import ZIP_DEFLATED, ZipFile

OUTPUT_DIR = Path.cwd()
CTA = "可关注「金赋补贴宝」，进入补贴平台，进行企业资质评估和政策匹配，获取更适合自身情况的补贴推荐清单。"
TITLE_MAX_CHARS = 30
OLD_TITLE_YEAR_RE = re.compile(r"20(?:0\d|1\d|2[0-4])年?")

# 默认只输出当前用户本轮提供的政策链接。
POLICY_URLS = [
    'http://hrss.gd.gov.cn/gkmlpt/content/3/3848/post_3848321.html',
    'http://hrss.gd.gov.cn/gkmlpt/content/3/3829/post_3829415.html',
    'http://zfcxjst.gd.gov.cn/gkmlpt/content/3/3237/post_3237631.html',
    'http://drc.gd.gov.cn/gkmlpt/content/1/1060/post_1060486.html',
    'http://mpa.gd.gov.cn/gkmlpt/content/2/2106/post_2106330.html',
    'http://zfcxjst.gd.gov.cn/gkmlpt/content/1/1457/post_1457103.html',
    'http://hrss.gd.gov.cn/gkmlpt/content/3/3265/post_3265129.html',
    'http://drc.gd.gov.cn/gkmlpt/content/0/864/post_864366.html',
    'http://gdjr.gd.gov.cn/gkmlpt/content/2/2269/post_2269667.html',
    'http://hrss.gd.gov.cn/gkmlpt/content/3/3776/post_3776746.html',
    'http://mpa.gd.gov.cn/gkmlpt/content/3/3271/post_3271247.html',
    'http://czt.gd.gov.cn/gkmlpt/content/3/3087/post_3087620.html',
    'http://mpa.gd.gov.cn/gkmlpt/content/2/2107/post_2107912.html',
    'http://gdjr.gd.gov.cn/gkmlpt/content/3/3668/post_3668706.html',
    'http://wsjkw.gd.gov.cn/gkmlpt/content/2/2127/post_2127713.html',
    'http://mpa.gd.gov.cn/gkmlpt/content/2/2108/post_2108916.html',
    'http://slt.gd.gov.cn/gkmlpt/content/1/1075/post_1075975.html',
    'http://mpa.gd.gov.cn/gkmlpt/content/2/2105/post_2105837.html',
    'http://sft.gd.gov.cn/gkmlpt/content/1/1140/post_1140262.html',
    'http://mpa.gd.gov.cn/zwgk/zcfg/fgjd/yaopin/content/post_3818440.html',
    'http://gdyjzx.gd.gov.cn/zcyj/zjsd/content/post_3520038.html',
    'http://czt.gd.gov.cn/gkmlpt/content/4/4232/post_4232862.html#98',
    'http://czt.gd.gov.cn/gkmlpt/content/4/4232/post_4232870.html#98',
    'http://czt.gd.gov.cn/gkmlpt/content/4/4233/post_4233927.html#86',
    'http://czt.gd.gov.cn/gkmlpt/content/4/4194/post_4194666.html#98',
    'http://www.gd.gov.cn/zwgk/gongbao/2021/30/content/post_3627117.html',
    'http://dara.gd.gov.cn/gkmlpt/content/4/4151/post_4151053.html#1602',
    'http://czt.gd.gov.cn/gkmlpt/content/4/4074/post_4074434.html#86',
    'http://czt.gd.gov.cn/gkmlpt/content/4/4067/post_4067988.html#86',
    'http://td.gd.gov.cn/gkmlpt/content/4/4028/post_4028350.html#1487',
    'http://czt.gd.gov.cn/gkmlpt/content/3/3055/post_3055821.html',
    'http://gdii.gd.gov.cn/gkmlpt/content/4/4016/post_4016613.html#2902',
    'http://edu.gd.gov.cn/gkmlpt/content/3/3987/post_3987646.html#1621',
    'http://hmo.gd.gov.cn/gkmlpt/content/3/3928/post_3928133.html',
    'http://gdwsxf.gd.gov.cn/zcfg/zcwj/content/post_3895832.html',
    'http://gdii.gd.gov.cn/gkmlpt/content/3/3551/post_3551296.html',
    'http://td.gd.gov.cn/gkmlpt/content/3/3572/post_3572563.html',
    'http://amr.gd.gov.cn/gkmlpt/content/2/2277/post_2277497.html',
    'http://hrss.gd.gov.cn/gkmlpt/content/3/3334/post_3334065.html',
    'http://zfcxjst.gd.gov.cn/gkmlpt/content/3/3326/post_3326848.html',
]
DEFAULT_VARIANTS_PER_URL = 1

SOURCE_BY_HOST = {
    "www.szlh.gov.cn": "深圳市罗湖区相关部门",
    "fgw.sz.gov.cn": "深圳市发展和改革委员会",
    "stic.sz.gov.cn": "深圳市科技创新局",
    "sf.sz.gov.cn": "深圳市政策法规检索平台",
    "commerce.sz.gov.cn": "深圳市商务局",
    "wtl.sz.gov.cn": "深圳市文化广电旅游体育局",
    "amr.sz.gov.cn": "深圳市市场监督管理局",
    "zjj.sz.gov.cn": "深圳市住房和建设局",
    "gdii.gd.gov.cn": "广东省工业和信息化厅",
    "gbdsj.gd.gov.cn": "广东省数据管理部门",
    "www.gd.gov.cn": "广东省人民政府",
    "czt.gd.gov.cn": "广东省财政厅",
    "hrss.gd.gov.cn": "广东省人力资源和社会保障厅",
    "dara.gd.gov.cn": "广东省农业农村厅",
    "gdstc.gd.gov.cn": "广东省科学技术厅",
    "gdjr.gd.gov.cn": "广东省地方金融管理局",
    "zfcxjst.gd.gov.cn": "广东省住房和城乡建设厅",
    "slt.gd.gov.cn": "广东省水利厅",
    "eea.gd.gov.cn": "广东省生态环境厅",
    "td.gd.gov.cn": "广东省交通运输厅",
    "gpcgd.gd.gov.cn": "广东省政府采购中心",
    "edu.gd.gov.cn": "广东省教育厅",
    "mpa.gd.gov.cn": "广东省药品监督管理局",
    "sft.gd.gov.cn": "广东省司法厅",
    "wsjkw.gd.gov.cn": "广东省卫生健康委员会",
    "hmo.gd.gov.cn": "广东省港澳事务办公室",
    "gdyjzx.gd.gov.cn": "广东省粤港澳大湾区研究院",
    "gdwsxf.gd.gov.cn": "广东省卫生健康相关部门",
    "amr.gd.gov.cn": "广东省市场监督管理局",
    "drc.gd.gov.cn": "广东省发展和改革委员会",
    "com.gd.gov.cn": "广东省商务厅",
    "zxqyj.sz.gov.cn": "深圳市中小企业服务局",
    "www.sz.gov.cn": "深圳市人民政府",
    "www.lg.gov.cn": "深圳市龙岗区相关部门",
    "lg.gov.cn": "深圳市龙岗区相关部门",
    "gxj.sz.gov.cn": "深圳市工业和信息化局",
    "pnr.sz.gov.cn": "深圳市规划和自然资源局",
    "www.baoan.gov.cn": "深圳市宝安区相关部门",
    "www.yantian.gov.cn": "深圳市盐田区相关部门",
    "www.szlhq.gov.cn": "深圳市龙华区相关部门",
    "qh.sz.gov.cn": "深圳市前海管理局",
    "www.szft.gov.cn": "深圳市福田区相关部门",
    "www.dpxq.gov.cn": "深圳市大鹏新区相关部门",
    "jr.sz.gov.cn": "深圳市地方金融管理局",
    "shenzhen.chinatax.gov.cn": "国家税务总局深圳市税务局",
    "szfb.sz.gov.cn": "深圳市地方金融管理局",
    "weather.sz.gov.cn": "深圳市气象局",
    "www.cjr.org.cn": "深圳市残疾人联合会",
    "meeb.sz.gov.cn": "深圳市生态环境局",
    "hsa.sz.gov.cn": "深圳市医疗保障局",
    "www.szns.gov.cn": "深圳市南山区相关部门",
    "www.szpsq.gov.cn": "深圳市坪山区相关部门",
    "cgj.sz.gov.cn": "深圳市城市管理和综合执法局",
    "wjw.sz.gov.cn": "深圳市卫生健康委员会",
    "tb.sz.gov.cn": "深圳市交通运输局",
}

SOURCE_BY_POST_ID = {
    "12778790": "深圳市工业和信息化局",
    "12584949": "深圳市住房和建设局、深圳市人力资源和社会保障局",
    "12658648": "深圳市发展和改革委员会、深圳市财政局、深圳市商务局",
    "12740127": "深圳市科技创新局等部门",
    "12647198": "深圳市龙岗区工业和信息化局",
    "12795315": "深圳市商务局",
    "12764271": "深圳市科技创新局",
    "12762397": "深圳市工业和信息化局",
    "12077746": "深圳市工业和信息化局",
    "11619789": "深圳市市场监督管理局",
    "12821085": "南山区工业和信息化局",
}


PLAN_BY_POST_ID = {
    "12821085": (
        "南山人才服务园房租补贴，最高100万先测匹配",
        "已入驻或计划持续经营于南山区人力资源服务产业园的人才服务机构、人力资源服务机构、拥有核心产品和成长性的知名服务企业及分支机构",
        "南山区人力资源服务产业园入驻机构、申请补贴时间段实际经营地在南山区、第一年和第二年70%租金补贴且每年最高100万元、第三年至第五年50%租金补贴且每年最高70万元、12个月为一个年度、每年申报一次、2023年至2024年接续周期租金、不含税租金、付款时间需在项目开通前、不得重复申报同类租赁补贴、无偿资助和事后补贴制",
        "营业执照、南山区经营证明、人力资源服务产业园入驻证明、租赁合同、租金发票、付款凭证、不含税租金明细、租金实际归属期说明、企业核心产品介绍、成长性和知名度证明、财务制度、信用记录、未重复申报承诺、数据申报证明",
    ),
}


SUBJECT_BY_POST_ID = {
    "12821085": "人才服务园房租补贴",
}


TITLE_VARIANTS_BY_POST_ID = {
    "12821085": [
        "人才服务园房租最高补100万",
        "南山入驻机构租金别白交",
        "70%房租补贴机会来了",
        "人才机构五年租金补贴怎么拿",
        "前两年最高100万别错过",
        "第三到第五年仍可补70万",
        "不含税租金补贴先测算",
        "人力资源机构降本看这里",
        "南山服务机构租金补贴清单",
        "入驻产业园补贴材料先备好",
    ],
}


FALLBACK_POLICY_BY_POST_ID = {
    "12821085": (
        "南山区促进产业高质量发展专项资金——区工业和信息化局分项资金南山人力资源服务产业园入驻机构房租补贴项目操作规程（2026年度）",
        "为支持拥有核心产品、成长性好、竞争力强、全球性或国内知名的人才服务机构入驻区人力资源服务产业园，南山区制定人力资源服务产业园入驻机构房租补贴项目操作规程。政策鼓励拥有核心产品、成长性好、竞争力强、全球性或国内知名的人才服务机构入驻区人力资源服务产业园。对经核准的入驻机构，在第一年和第二年每年按实际支付租金的70%给予最高100万元租金补贴，在第三年、第四年和第五年每年按实际支付租金的50%给予最高70万元租金补贴。申请房租补贴从首次申请起连续计算，以12个月为一个年度，每年申报一次。本项资助属于核准类项目，采取无偿资助方式和事后补贴制，受资助项目无需验收，受年度资金预算控制。项目开通是对企业2023年至2024年1年接续上一次申报周期的租金不含税给予补贴，以租金实际归属期为准，付款时间需在项目开通前。申请主体应为申请补贴时间段实际经营地在南山区的人力资源服务产业园入驻机构含分支机构，需履行相关数据申报义务、守法经营、诚实守信、有规范财务管理制度。本项目不得与辖区其他同类性质租赁补贴政策重复申报，也不得与前海合作区制定的同类性质扶持政策重复申报。被纳入严重失信主体名单或失信惩戒措施清单的，以及申请后项目实施地或数据申报地发生变化不再符合条件的，不予资助。"
    ),
}


PROMOTION_PLANS = [('省级政策有新信号，企业先找补贴切入口', '广东科技、制造、商贸、农业和现代服务业企业', '省级政策导向、支持对象、资金范围、项目条件、申报窗口和绩效管理', '政策台账、项目清单、财务资料、合同票据、资质证书、成果案例和责任分工'),
 ('外贸和商贸企业看政策，要把订单变成申报证据', '广东外贸企业、跨境电商、商贸流通、品牌出海和服务贸易企业', '外贸稳增长、市场开拓、品牌培育、展会活动、订单数据和财政支持', '订单合同、报关或物流资料、销售数据、参展材料、宣传素材、发票付款和复盘报告'),
 ('省级文件别只转发，企业要看能不能拿补贴', '广东成长型企业、产业园区、科技制造和服务业企业', '政策对象、资金安排、产业方向、材料要求、项目周期和监督责任', '企业画像、项目储备、费用台账、合同票据、信用记录、绩效说明和申报计划'),
 ('人社新通知来了，用工企业要盯紧补贴条件', '广东用工企业、人力资源服务机构、创业团队和就业服务主体', '就业补贴、社保缴纳、岗位吸纳、人员条件、申请材料和诚信承诺', '员工花名册、劳动合同、社保记录、工资流水、招聘证明、人员名单和申请表'),
 ('省级政策再次更新，重复链接也别重复做材料', '广东多项目申报企业、财务负责人和政策专员', '政策去重、项目匹配、资金价值、材料口径、费用边界和申报优先级', '政策清单、项目台账、费用明细、合同发票、付款凭证、材料缺口表和责任人'),
 ('农业政策窗口打开，涉农企业别只看项目名称', '广东农业企业、农产品加工、乡村运营、农业科技和合作社主体', '农业项目、乡村产业、品牌建设、示范基地、设备投入和财政奖补', '基地资料、生产记录、采购合同、销售台账、认证证书、照片视频和绩效说明'),
 ('科技通知发布后，研发企业先补证据链', '广东科技型企业、高新技术企业、研发平台和成果转化团队', '科技创新、研发投入、项目立项、成果转化、知识产权和资金补助', '研发立项书、研发费用台账、知识产权、检测报告、成果证明、合同发票和人员材料'),
 ('政府公报里的政策，企业要转成补贴日历', '广东科技、制造、农业、商贸、文旅和服务业企业', '公报文件、政策有效期、资金方向、主管部门、申报节点和后续监督', '政策日历、项目储备表、财务报表、合同票据、资质证书、成果材料和内部分工'),
 ('发改类政策看方向，企业项目储备要跟上', '广东先进制造、现代服务、基础设施、节能低碳和产业平台企业', '发展规划、产业方向、项目投资、要素保障、资金安排和绩效目标', '项目建议书、备案材料、投资台账、合同票据、能耗数据、成果说明和责任分工'),
 ('卫健类政策不只医院看，相关企业也要看服务场景', '广东医疗健康、智慧医疗、医养服务、器械药品和信息化企业', '医疗服务、卫生健康、信息化建设、服务能力、项目合规和财政支持', '服务方案、资质证书、系统合同、采购票据、人员资料、应用数据和成效报告'),
 ('法治政策影响申报，合规底子要提前打牢', '广东拟申报补贴、资质认定、政府项目和公共服务的企业', '法规依据、材料真实性、信用记录、内部制度、项目监督和责任边界', '内控制度、合同台账、财务凭证、信用记录、审批资料、项目档案和整改说明'),
 ('药品监管政策更新，医药企业材料要更细', '广东药品、医疗器械、化妆品、生物医药和流通企业', '注册备案、质量管理、检验检测、生产流通、合规记录和创新项目', '注册证书、检测报告、质量体系文件、生产记录、销售合同、发票付款和风险说明'),
 ('医疗卫生项目要申报，服务数据和合规资料都要留', '广东医疗机构、健康服务企业、医疗信息化和医药器械企业', '医疗服务能力、公共卫生、项目投入、人员资质、服务数据和资金使用', '服务台账、人员证书、采购合同、发票付款、系统截图、服务数据和绩效报告'),
 ('教育类政策里，也有企业服务和项目机会', '广东教育服务企业、校企合作机构、培训服务商和科技企业', '教育项目、校企合作、信息化建设、培训服务、资质要求和绩效成果', '合作协议、课程方案、人员名单、服务合同、发票付款、成果材料和满意度数据'),
 ('老政策也别忽略，企业合规申报要看基础规则', '广东各类长期申报补贴、奖励、资质和专项资金的企业', '基础规则、申报条件、材料真实性、资金使用、信用管理和监督检查', '历史申报档案、合同票据、财务资料、信用记录、制度文件、绩效报告和归档清单'),
 ('采购政策一变化，供应商要整理投标和履约证据', '广东政府采购供应商、软件服务商、设备供应商和公共服务机构', '政府采购、供应商资格、合同履约、价格证明、信用记录和资金支付', '投标文件、中标通知、采购合同、验收报告、发票付款、服务记录和信用证明'),
 ('药械政策看似专业，企业申报也要抓质量证据', '广东药械企业、检测机构、研发服务商和医疗健康企业', '药械注册、质量检测、临床评价、生产许可、创新产品和监管合规', '注册资料、检测报告、临床资料、质量体系、生产记录、合同发票和成果说明'),
 ('科技成果要转化，项目证明不能只靠口头描述', '广东科技企业、高校院所合作项目、成果转化平台和创新团队', '科技成果、转化应用、研发费用、知识产权、合作开发和项目验收', '成果证明、知识产权、合作协议、研发费用、检测报告、销售合同和验收资料'),
 ('省级规则沉淀下来，企业申报少走弯路', '广东企业管理层、财务负责人、项目负责人和政策申报团队', '政策适配、项目事实、费用边界、材料口径、绩效目标和合规管理', '企业制度、项目清单、费用明细、合同票据、付款凭证、信用记录和复盘报告'),
 ('交通运输政策来了，物流企业要把运营数据留住', '广东交通运输、物流仓储、供应链服务、港航和平台企业', '运输服务、物流效率、车辆船舶、数字化管理、安全合规和资金支持', '运营台账、车辆或船舶资料、运输合同、发票付款、系统数据、安全记录和绩效说明'),
 ('公共卫生项目做过了，别忘了沉淀补贴材料', '广东医疗健康、公共卫生、检测服务、医养和健康管理企业', '公共卫生、服务能力、设备采购、人员资质、服务数量和资金绩效', '服务记录、设备合同、人员证书、发票付款、数据报表、现场照片和总结报告'),
 ('医药监管细节多，创新企业要把合规变成优势', '广东生物医药、医疗器械、化妆品和药品流通企业', '质量合规、注册备案、研发创新、检测认证、生产流通和风险管理', '质量体系、注册证书、检测报告、研发资料、生产记录、销售合同和内审记录'),
 ('省级规范文件更新，企业申报口径要同步检查', '广东科技、制造、商贸、农业、医药和服务业企业', '规范文件、政策口径、支持对象、材料边界、资金监管和信用要求', '政策台账、材料清单、合同票据、财务报表、资质证书、信用记录和内部流程'),
 ('药品经营企业看政策，进销存和质量记录很关键', '广东药品经营、医药流通、连锁药店和供应链企业', '药品经营、质量追溯、进销存管理、人员资质、信用监管和合规成本', '进销存台账、质量制度、人员证书、采购合同、销售发票、冷链记录和整改材料'),
 ('药械项目申报前，检测和注册资料要先归档', '广东医疗器械、药品研发、检测机构和创新产品企业', '注册申报、检测验证、研发投入、质量体系、市场应用和监管记录', '注册资料、检测报告、研发费用、质量体系文件、销售合同、客户案例和验收材料'),
 ('生态环保政策也能带来项目机会，绿色投入要留痕', '广东绿色制造、节能环保、园区运营、污染治理和低碳服务企业', '生态环境、污染治理、节能降碳、绿色项目、设备投入和绩效监测', '环评资料、设备合同、监测报告、发票付款、能耗数据、治理成效和验收材料'),
 ('水利项目看起来远，相关企业也要准备工程证据', '广东水利工程、智慧水务、设备供应、生态治理和施工服务企业', '水利建设、工程管理、设备投入、项目验收、安全记录和资金监管', '工程合同、施工记录、设备清单、发票付款、验收资料、安全台账和绩效报告'),
 ('交通项目不是只看建设，服务和安全也能成证据', '广东物流运输、交通服务、工程建设和平台运营企业', '交通建设、运输服务、安全管理、数字化应用、合同履约和项目成效', '项目合同、运营数据、安全记录、设备清单、发票付款、验收资料和服务报告'),
 ('卫健政策再细，也要回到企业服务场景', '广东医疗健康、养老服务、健康信息化、药械和公共服务企业', '卫生健康、服务能力、信息化建设、人员资质、设备投入和数据成效', '服务方案、人员证书、采购合同、系统截图、发票付款、数据报表和成效材料'),
 ('卫生健康项目要讲清楚，服务对象和结果都要有', '广东医疗机构、健康管理、检测服务、医养结合和信息化企业', '健康服务、项目实施、服务对象、费用归集、人员配置和绩效评价', '服务台账、人员名单、合同票据、设备资料、服务数据、满意度记录和总结报告'),
 ('医疗机构能力建设，项目台账越早做越好', '广东医疗机构、医疗服务商、智慧医疗和医药器械企业', '能力建设、设备采购、信息化系统、人员培训、服务成效和资金使用', '设备合同、系统合同、人员培训记录、发票付款、服务数据、验收资料和绩效报告'),
 ('药品安全政策下，企业别让合规资料散落各处', '广东药品、医疗器械、化妆品和医药流通企业', '药品安全、质量追溯、监管检查、人员资质、风险控制和整改闭环', '质量制度、检查记录、人员证书、采购销售台账、整改报告、检测资料和内审记录'),
 ('药械流通企业看政策，信用和追溯资料别缺', '广东药械流通、批发零售、医疗服务供应商和平台企业', '流通监管、质量追溯、信用记录、人员资质、合同履约和风险控制', '经营资质、进销存台账、合同发票、冷链记录、人员证书、信用记录和整改说明'),
 ('医疗卫生改革推进，相关服务企业要找配套机会', '广东医疗服务、健康管理、医药器械、信息化和养老服务企业', '医改方向、服务能力、项目投入、信息化建设、绩效评价和资金支持', '服务方案、项目台账、设备合同、系统截图、发票付款、人员资料和成效报告'),
 ('住建类政策出现，工程企业要先整理项目档案', '广东建筑施工、工程咨询、园区运营、物业服务和绿色建筑企业', '工程管理、绿色建筑、项目建设、资质等级、合同履约和资金支持', '工程合同、施工记录、验收资料、资质证书、发票付款、现场照片和绩效说明'),
 ('财政资金规则基础但重要，企业不能只让财务看', '广东拟申报专项资金、补助、奖励和贴息的企业', '财政资金、预算绩效、申报审核、拨付管理、监督检查和材料真实性', '预算表、绩效目标、合同票据、付款凭证、财务报表、审计资料和项目总结'),
 ('药监政策换口径，企业注册和质量资料要同步更新', '广东药品、医疗器械、化妆品、检测认证和研发服务企业', '注册备案、质量体系、检验检测、生产经营、风险管理和创新应用', '注册证书、检测报告、质量制度、生产记录、经营台账、合同发票和整改材料'),
 ('科技平台政策下，创新资源要变成可申报项目', '广东科技平台、孵化器、研发机构、企业研发中心和创新团队', '科技平台、研发服务、成果转化、项目投入、知识产权和绩效评价', '平台资质、服务台账、研发合同、知识产权、费用凭证、成果案例和绩效报告'),
 ('教育服务项目也要留证据，校企合作别只签协议', '广东教育服务企业、职业教育、校企合作机构和科技服务商', '教育服务、校企合作、培训项目、信息化建设、人员培养和项目成效', '合作协议、课程资料、人员名单、培训记录、服务合同、发票付款和成果证明'),
 ('教育资金和项目管理，学校服务企业也要看机会', '广东教育信息化、培训服务、校园服务、设备供应和校企合作企业', '教育项目、资金管理、设备采购、培训服务、绩效目标和材料要求', '项目方案、采购合同、发票付款、课程记录、验收资料、服务数据和总结报告'),
 ('教育政策连续调整，服务商要提前备好案例', '广东教育服务商、数字校园、培训机构、设备供应和内容服务企业', '教育政策、服务资质、项目案例、合同履约、绩效成果和合规记录', '服务案例、合作协议、合同发票、人员资料、课程成果、验收报告和满意度记录'),
 ('财政资金管理办法里，藏着申报成败的细节', '广东企业财务、项目负责人、园区平台和专项资金申报主体', '资金管理、项目预算、绩效评价、监督审计、材料真实性和信息公开', '资金台账、预算表、合同票据、付款凭证、绩效报告、审计资料和归档清单'),
 ('药械创新企业别只盯研发，监管材料也要同步准备', '广东药械研发、创新医疗器械、注册服务和检测机构', '创新产品、注册审评、质量体系、临床评价、检测验证和市场应用', '研发资料、注册资料、检测报告、临床评价、质量制度、销售合同和应用证明'),
 ('金融政策看监管，也看企业融资证据', '广东金融服务机构、科技企业、拟上市企业、融资平台和担保机构', '金融监管、融资支持、贷款贴息、风险补偿、上市培育和信用管理', '授信文件、融资合同、利息凭证、担保资料、财务报表、资金用途和信用记录'),
 ('地方金融服务企业，服务实体经济要有数据证明', '广东金融机构、融资服务平台、担保小贷机构和产业服务机构', '金融服务、实体经济支持、客户服务、风险防控、合规经营和数据报送', '客户台账、服务合同、授信记录、风险说明、财务报表、制度文件和数据报送材料'),
 ('财政补助资金到位前，企业要把项目事实讲清楚', '广东科技、制造、农业、医药、教育和公共服务项目企业', '补助资金、项目事实、费用归集、绩效目标、资金拨付和后续核查', '项目说明、费用台账、合同发票、付款凭证、绩效数据、验收材料和承诺书'),
 ('省级政策回到申报，拼的是平时材料管理', '广东各类准备申报补贴、奖励、资质和专项资金的企业', '政策适配、项目证据、费用归集、申报条件、绩效成果和合规管理', '项目档案、费用台账、合同发票、付款凭证、资质证书、成果材料和复盘报告')]

class HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"script", "style", "template", "noscript"}:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "template", "noscript"} and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        text = data.strip()
        if text:
            self.parts.append(text)

    def get_text(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self.parts)).strip()


def strip_html(raw_html: str) -> str:
    parser = HTMLTextExtractor()
    parser.feed(unescape(raw_html or ""))
    return parser.get_text()


BOILERPLATE_KEYWORDS = (
    "无障碍",
    "长者助手",
    "我的收藏",
    "收藏",
    "政府信息公开",
    "政策文件",
    "宝安区人民政府门户网站",
    "进入关怀版",
    "关怀版",
    "繁體版",
    "简体版",
    "政务公开",
    "网站首页",
    "政务服务",
    "政民互动",
    "美丽宝安",
    "当前位置",
    "履职依据",
    "科技创新局",
    "规章库",
    "规章",
    "高级搜索",
    "搜索以下关键词",
    "搜索位置",
    "搜索",
    "排序方式",
    "按时间",
    "按相关度",
    "文件状态",
    "现行有效",
    "已失效",
    "全文",
    "标题",
    "不限",
    "收起",
    "下载文字版",
    "下载图片版",
    "索引号",
    "字体",
    "大 中 小",
    "大中小",
    "打印",
    "分享",
    "发布日期",
    "发布时间",
    "信息来源",
    "稿件来源",
    "附件",
    "首页",
    "工业和信息化局",
    "信息公开",
    "办公室",
    "印发",
)


def remove_urls(text: str) -> str:
    return re.sub(r"https?://\S+", "", text or "").strip()


def has_boilerplate(text: str) -> bool:
    return sum(1 for keyword in BOILERPLATE_KEYWORDS if keyword in text) >= 2


def clean_policy_text(text: str) -> str:
    cleaned = remove_urls(re.sub(r"\s+", " ", text or "")).strip()
    cleaned = re.sub(r"[|>]+", " ", cleaned)
    cleaned = re.sub(r"\bEN\b", " ", cleaned)
    for keyword in sorted(BOILERPLATE_KEYWORDS, key=len, reverse=True):
        cleaned = cleaned.replace(keyword, " ")
    return re.sub(r"\s+", " ", cleaned).strip(" -_|：:，。 ")


def policy_summary(text: str, limit: int = 180) -> str:
    raw = remove_urls(re.sub(r"\s+", " ", text or "")).strip()
    positions = [raw.find(keyword) for keyword in BOILERPLATE_KEYWORDS if raw.find(keyword) >= 0]
    if positions and min(positions) < 80:
        return ""
    if positions:
        raw = raw[: min(positions)].strip()
    cleaned = clean_policy_text(raw)
    if not cleaned or has_boilerplate(cleaned):
        return ""
    sentences = [part.strip() for part in re.split(r"(?<=[。！？；])", cleaned) if part.strip()]
    summary = ""
    for sentence in sentences:
        if has_boilerplate(sentence):
            continue
        if len(summary) + len(sentence) > limit and summary:
            break
        summary += sentence
        if len(summary) >= 80:
            break
    summary = summary or cleaned[:limit]
    return summary[:limit].strip(" ，。；：")


def fetch_url_text(url: str) -> tuple[str, str]:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=12) as response:
        raw = response.read()
        charset = response.headers.get_content_charset() or "utf-8"
    html = raw.decode(charset, errors="replace")
    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.I | re.S)
    title = strip_html(title_match.group(1)) if title_match else ""
    text = clean_policy_text(strip_html(html))
    return title, text


def host_from_url(url: str) -> str:
    match = re.search(r"https?://([^/]+)", url)
    return match.group(1).lower() if match else ""


def post_id_from_url(url: str) -> str:
    match = re.search(r"post_(\d+)", url)
    if match:
        return match.group(1)
    match = re.search(r"/(\d+)\.html", url)
    return match.group(1) if match else "policy"


def source_from_url(url: str) -> str:
    post_source = SOURCE_BY_POST_ID.get(post_id_from_url(url))
    if post_source:
        return post_source
    return SOURCE_BY_HOST.get(host_from_url(url), "政策发布部门")


def topic_for_source(source: str, url: str) -> tuple[str, str, str]:
    if "文化" in source or "旅游" in source or "体育" in source:
        return (
            "文旅体育补贴机会：企业如何把扶持信息变成增长机会？",
            "从文旅体育类政策原文看，企业应重点拆解支持对象、项目类型、活动周期、投入费用、宣传效果、客流或参与数据、安全管理、社会效益和绩效评价等要素。文化演艺、旅游服务、体育赛事、文创活动、数字文旅、场馆运营和公共文化服务主体，不能只关注政策是否提到补贴，更要判断自身项目能否用合同、票据、现场资料、传播数据和用户反馈证明真实投入与实际成效。",
            "深圳金赋服务这类企业时，会先用补贴平台匹配市、区两级文旅体育、促消费、品牌活动、赛事展演、数字化改造和经营主体培育政策，再通过补贴平台生成申报优先级、材料清单和时间表。企业可以把一次活动的预算、合同、发票、照片、宣传稿、客流统计和复盘报告统一沉淀，后续遇到同类政策时就能快速判断是否申报，减少临时补材料的压力。",
        )
    if "市场监督" in source:
        return (
            "质量标准补贴机会：企业如何把合规能力变成资金机会？",
            "市场监管类政策原文通常围绕质量提升、标准建设、知识产权、品牌培育、食品安全、计量认证、检验检测、质量奖项或专项资金管理展开。企业需要重点看企业主体、资质证书、项目投入、标准文本、检测报告、专利商标、认证证明、合同发票、付款凭证、项目成果和信用记录等要求。对食品、消费品、制造业、检测机构和平台型企业来说，日常合规资料越完整，后续申报成功率越高。",
            "深圳金赋会把市场监管政策与企业的质量管理、品牌建设、知识产权、标准化、食品安全和检测认证台账结合起来。补贴平台可帮助企业识别适合申报的质量提升、标准研制、知识产权保护、品牌培育和安全追溯类项目，并提醒企业提前补齐证明材料、费用归集和成果说明，让合规投入不只是成本，也能转化为政策资金和品牌背书。",
        )
    if "住房" in source:
        return (
            "住建领域补贴机会：建筑和园区企业如何提前做好项目台账？",
            "住建类政策原文往往涉及建筑业、工程管理、住房保障、城市更新、绿色建筑、物业服务、人才住房、工程质量安全或行业规范。企业要重点核验项目所在地、合同主体、建设周期、资质等级、工程资料、验收文件、费用支出、人员社保、信用记录和绩效要求。很多住建政策看似偏管理，但背后常常关系到资质培育、项目备案、奖励补贴、人才安居和绿色低碳专项。",
            "深圳金赋可帮助建筑施工、工程咨询、园区运营、物业服务和住房相关企业，把住建政策与企业资质、项目合同、工程节点、人才政策、绿色建筑、数字化管理和专项补贴进行组合匹配。通过补贴平台，企业可以建立项目级材料清单，提前归档合同、发票、付款、验收、人员和信用资料，避免等申报通知发布后才发现关键文件缺失。",
        )
    if "工业" in source or "中小企业" in source:
        return (
            "工信和中小企业补贴机会：企业如何找到申报路径？",
            "工信和中小企业政策原文通常覆盖技术改造、数字化转型、专精特新、产业集群、软件信息、绿色制造、首版次产品、智能制造、融资服务和企业梯度培育。企业要重点看支持范围、项目建设期、投入下限、资助比例、认定名单、设备和软件费用、研发投入、知识产权、财务数据、合同发票、付款凭证和应用成效。只看最高金额容易误判，真正决定申报价值的是项目与政策条件的匹配度。",
            "深圳金赋的补贴平台沉淀1100万条全国四级政策数据，可按区域、行业、营收、研发投入、知识产权、人员规模和项目阶段做标签匹配。并进一步帮助企业形成年度申报地图，判断先做专精特新、高新技术、技改补贴、数字化转型、软件项目还是产业专项，并将申报材料拆成企业内部可以执行的SOP。",
        )
    if "金融" in source:
        return (
            "金融支持补贴机会：企业如何把融资动作转化为政策支持？",
            "金融类政策原文通常与贷款贴息、融资担保、上市培育、产业基金、绿色金融、风险补偿、金融机构服务实体经济或地方金融监管有关。企业需要重点梳理融资合同、授信文件、利息凭证、担保资料、财务报表、纳税社保、资金用途、项目进展和信用记录。对于成长型企业来说，融资不是孤立动作，应与研发投入、产业项目、资质培育和市场扩张同步规划。",
            "深圳金赋可帮助企业把金融政策与研发补贴、产业扶持、专精特新、人才政策和区级配套联动起来，形成资金规划和申报节奏。补贴平台可提示企业哪些贷款、担保、上市培育或基金项目需要提前留存凭证，哪些政策可以与产业项目形成组合，帮助企业降低融资成本、提高政策资金获取效率。",
        )
    return (
        "政策补贴机会：企业如何快速判断是否值得申报？",
        "面对一条新政策，企业首先要从原文中拆出发布部门、适用区域、支持对象、申报时间、资助标准、费用范围、材料要求、审核方式和不重复享受限制。很多企业只看政策名称或最高金额，容易忽略项目周期、主体资质、合同票据、绩效目标和材料一致性。真正适合申报的政策，必须能落到企业现有资质、项目投入和证明材料上。",
        "深圳金赋科技有限公司依托补贴平台沉淀1100万条全国四级公开政策数据，并通过补贴平台提供政策匹配、资质测评、申报清单和节点提醒。企业可以先做一次政策体检，判断这条政策与自身行业、规模、项目阶段和材料基础是否匹配，再决定是否进入正式申报准备，避免盲目投入时间和成本。",
    )


TITLE_NOISE_WORDS = (
    "深圳政府在线",
    "深圳市人民政府门户网站",
    "宝安区人民政府门户网站",
    "政府在线",
    "信息公开",
    "政务公开",
    "网站首页",
    "当前位置",
    "政策文件",
    "政策法规",
    "通知公告",
)


def clean_policy_title(title: str) -> str:
    raw = remove_urls(re.sub(r"\s+", " ", title or "")).strip(" -_|：:，。")
    if not raw or "$" in raw or "function" in raw.lower():
        return ""
    raw = re.split(r"[|_]+", raw)[0].strip(" -—_|")
    for suffix in ("-深圳政府在线", "_深圳政府在线", "-深圳市人民政府门户网站", "_深圳市人民政府门户网站"):
        raw = raw.replace(suffix, "")
    for word in TITLE_NOISE_WORDS:
        raw = raw.replace(word, " ")
    raw = re.sub(r"\s+", " ", raw).strip(" -—_|")
    if len(raw) < 6 or len(raw) > 120:
        return ""
    if has_boilerplate(raw) and not any(token in raw for token in ("通知", "办法", "措施", "规定", "方案", "细则", "指南")):
        return ""
    return raw[:90]


def short_policy_subject(policy_title: str) -> str:
    if not policy_title:
        return ""
    quoted = re.search(r"《([^》]{4,38})》", policy_title)
    if quoted:
        return quoted.group(1).strip()
    subject = policy_title
    subject = re.sub(r"^(深圳市|深圳|福田区|南山区|龙华区|盐田区|大鹏新区|前海|国家税务总局深圳市税务局)", "", subject)
    subject = re.sub(r".*?关于", "", subject)
    subject = re.sub(r"(的通知|通知|办法|规定|措施|细则|方案|指南)$", "", subject)
    subject = re.sub(r"[\s,，。；;：:]+", "", subject)
    return subject[:24]


def policy_excerpt(text: str, limit: int = 220) -> str:
    cleaned = clean_policy_text(text)
    if not cleaned:
        return ""
    sentences = [part.strip(" ，。；：") for part in re.split(r"(?<=[。！？；])", cleaned) if part.strip()]
    keywords = ("扶持", "支持", "资助", "补贴", "奖励", "申报", "企业", "项目", "资金", "产业", "人才", "金融", "税", "住房", "商务", "创新")
    selected: list[str] = []
    for sentence in sentences:
        if has_boilerplate(sentence) or len(sentence) < 22 or len(sentence) > 180:
            continue
        if any(keyword in sentence for keyword in keywords):
            selected.append(sentence)
        if len(selected) >= 2:
            break
    if not selected:
        for sentence in sentences:
            if not has_boilerplate(sentence) and 22 <= len(sentence) <= 180:
                selected.append(sentence)
            if len(selected) >= 2:
                break
    excerpt = "。".join(selected)[:limit]
    return excerpt.strip(" ，。；：")


def subsidy_highlight(text: str, limit: int = 150) -> str:
    cleaned = clean_policy_text(text)
    if not cleaned:
        return ""
    sentences = [part.strip(" ，。；：") for part in re.split(r"(?<=[。！？；])", cleaned) if part.strip()]
    money_pattern = re.compile(r"(最高|不超过|给予|资助|补贴|奖励|贴息|扶持)[^。！？；]{0,55}?(万元|元|%|％)")
    support_words = ("资助", "补贴", "奖励", "扶持", "贴息", "资金", "补助")
    for sentence in sentences:
        if has_boilerplate(sentence) or len(sentence) > 180:
            continue
        if any(word in sentence for word in support_words) and money_pattern.search(sentence):
            return sentence[:limit].strip(" ，。；：")
    for sentence in sentences:
        if has_boilerplate(sentence) or len(sentence) > 180:
            continue
        if any(word in sentence for word in support_words):
            return sentence[:limit].strip(" ，。；：")
    return ""

def remove_old_title_years(text: str) -> str:
    cleaned = OLD_TITLE_YEAR_RE.sub("", text or "")
    cleaned = re.sub(r"[，,、：:；;\s]+", "，", cleaned)
    return cleaned.strip(" ，,、：:；;-—_（）()[]【】")


def normalize_article_title(title: str, fallback: str = "企业补贴机会，先做评估") -> str:
    cleaned = remove_old_title_years(title)
    if not cleaned:
        cleaned = remove_old_title_years(fallback) or "企业补贴机会，先做评估"
    cleaned = re.sub(r"\s+", "", cleaned).strip(" ，,、：:；;-—_（）()[]【】")
    return cleaned[:TITLE_MAX_CHARS] or "企业补贴机会，先做评估"


def make_article_title(plan_title: str, policy_title: str, index: int) -> str:
    raw_subject = remove_old_title_years(short_policy_subject(policy_title))
    if not raw_subject or len(raw_subject) < 4:
        return normalize_article_title(plan_title)
    subject = raw_subject[:14]
    templates = [
        f"{subject}背后，企业要看到补贴线索",
        f"{subject}来了，别只收藏文件",
        f"读懂{subject}，先看企业能不能匹配",
        f"{subject}不只是通知，也是项目提醒",
        f"围绕{subject}，企业要提前整理证据",
        f"{subject}释放信号，项目资料要跟上",
        f"别错过{subject}里的资金机会",
        f"{subject}怎么用？企业先做匹配",
        f"从{subject}看企业补贴准备",
        f"{subject}落地前，先盘点项目",
        f"看到{subject}，老板要问这几个问题",
        f"{subject}来了，财务资料别掉链子",
        f"企业关注{subject}，重点不止金额",
        f"{subject}背后藏着申报节奏",
        f"拿{subject}做一次补贴体检",
        f"{subject}适合谁？先看项目证据",
        f"别把{subject}只当政策新闻",
        f"{subject}能不能申，材料说了算",
        f"围绕{subject}，把投入变成证据",
        f"{subject}提醒企业提前留痕",
        f"从{subject}找到下一笔补贴线索",
        f"{subject}发布后，企业别等截止才看",
        f"{subject}里的机会，要用项目承接",
        f"企业读{subject}，先看自身条件",
        f"{subject}不难读，难在资料够不够",
        f"把{subject}放进年度补贴清单",
        f"{subject}来了，先别急着写材料",
        f"{subject}能否变现，关键看匹配度",
        f"{subject}适配度，先交给补贴平台",
        f"借{subject}梳理企业政策资产",
        f"{subject}不是终点，是申报起点",
        f"从{subject}看项目投入能否拿补贴",
        f"{subject}里的支持方向别看漏",
        f"{subject}窗口前，企业先补短板",
        f"围绕{subject}，做一张项目证据表",
        f"{subject}老板先看这一条",
        f"{subject}对企业意味着什么",
        f"不要只转发{subject}，要做评估",
        f"{subject}出现后，资料库要动起来",
        f"用{subject}检查企业申报底子",
        f"{subject}里的补贴信号怎么抓",
        f"从{subject}倒推材料准备",
        f"{subject}能不能拿，先看证据链",
        f"{subject}给企业的现实提醒",
        f"看完{subject}，项目台账要更新",
        f"{subject}背后是资金和材料边界",
        f"{subject}别只看标题，要看口径",
        f"企业借{subject}重新盘点投入",
        f"{subject}来了，补贴评估先行",
        f"围绕{subject}，把政策变成清单",
        f"{subject}可能对应哪些企业投入",
        f"读{subject}，先别被文件名带偏",
        f"{subject}提醒企业把票据留好",
        f"从{subject}看企业资质培育",
        f"{subject}发布，别错过配套机会",
        f"{subject}和企业补贴有什么关系",
        f"把{subject}翻译成企业行动",
        f"{subject}不是冷文件，是资金线索",
        f"{subject}来了，先测一测能不能申",
        f"企业围绕{subject}做一次政策体检",
        f"聊{subject}，先看补贴机会",
        f"围绕{subject}，别少了申报评估",
        f"{subject}能帮企业拿补贴吗",
        f"拿补贴前，先看{subject}匹配度",
        f"{subject}里的贴息机会别漏看",
        f"企业想拿补贴，先看{subject}",
        f"{subject}别只读，先测补贴机会",
        f"把{subject}讲成补贴机会",
        f"{subject}里的申报机会怎么抓",
        f"围绕{subject}，帮企业找补贴",
    ]
    start = (index - 1) % len(templates)
    for offset in range(len(templates)):
        title = remove_old_title_years(templates[(start + offset) % len(templates)]).replace(" ", "")
        if title and 10 <= len(title) <= TITLE_MAX_CHARS:
            return title
    fallback_title = normalize_article_title(plan_title)
    if len(fallback_title) < 10:
        fallback_title = f"{fallback_title}补贴机会"
    return fallback_title[:TITLE_MAX_CHARS]

def policy_year(text: str) -> str:
    match = re.search(r"(20\d{2})年", text or "")
    return match.group(1) if match else ""


def readable_policy_subject(policy_title: str) -> str:
    subject = short_policy_subject(policy_title)
    if not subject:
        return ""
    subject = re.sub(r"^(安排|下达|提前下达|拨付|转发|印发|发布|组织申报|开展|做好)", "", subject)
    subject = re.sub(r"^\d{4}年(?:第[一二三四五六七八九十0-9]+批)?", "", subject)
    subject = re.sub(r"^(?:第[一二三四五六七八九十0-9]+批)?(?:中央|省级|市级|区级)?财政", "", subject)
    subject = re.sub(r"(补助资金预算|资金预算|预算)$", "资金", subject)
    subject = subject.strip(" ，。；：:、-—_（）()[]【】")
    keyword_subjects = [
        ("医疗服务与保障能力", "医疗服务与保障能力资金"),
        ("就业", "就业补贴政策"),
        ("创业", "创业补贴政策"),
        ("技能", "技能人才补贴"),
        ("人才", "人才服务补贴"),
        ("科技", "科技项目资金"),
        ("农业", "农业项目资金"),
        ("工业", "工业企业扶持"),
        ("制造", "制造业扶持"),
        ("财政", "财政资金政策"),
        ("数据", "数据要素政策"),
        ("数字", "数字化项目政策"),
        ("成果", "科技成果转化"),
    ]
    for keyword, label in keyword_subjects:
        if keyword in subject:
            return label
    return subject[:18]


def make_db_article_title(policy_title: str, article_suffix: str) -> str:
    subject = readable_policy_subject(policy_title)
    year = policy_year(policy_title)
    if year and int(year) < 2025:
        year = ""
    if subject:
        subject = normalize_article_title(subject)[:14]
        prefix = f"{year}年{subject}" if year and not subject.startswith(year) else subject
        candidates = [
            f"{prefix}，企业要看补贴口径",
            f"{prefix}别只收藏，先做申报评估",
            f"围绕{prefix}，企业要提前备材料",
            f"{prefix}能不能拿补贴",
            f"{prefix}贴息补贴别漏看",
        ]
        for candidate in candidates:
            title = remove_old_title_years(candidate).replace(" ", "")
            if title and len(title) <= TITLE_MAX_CHARS:
                return title
        return normalize_article_title(prefix)
    cleaned_suffix = article_suffix.rstrip("？?")
    return normalize_article_title(cleaned_suffix, "企业补贴机会，先做评估")

def clean_fetched_title(title: str) -> str:
    raw_title = remove_urls(re.sub(r"\s+", " ", title or "")).strip(" -_|")
    if any(keyword in raw_title for keyword in BOILERPLATE_KEYWORDS):
        return ""
    title = clean_policy_text(raw_title)
    if not title or "$" in title or "function" in title.lower() or len(title) > 80:
        return ""
    for suffix in ("_深圳政府在线", "-深圳政府在线", "_深圳市人民政府门户网站", "-深圳市人民政府门户网站"):
        title = title.replace(suffix, "")
    return title.strip()


def build_article_from_url(url: str, index: int) -> dict[str, object]:
    source = source_from_url(url)
    plan = PLAN_BY_POST_ID.get(post_id_from_url(url)) or (PROMOTION_PLANS[index - 1] if index - 1 < len(PROMOTION_PLANS) else PROMOTION_PLANS[-1])
    planned_title, audience, policy_focus, proof_materials = plan
    fetched_title = ""
    fetched_text = ""
    post_id = post_id_from_url(url)
    fallback = FALLBACK_POLICY_BY_POST_ID.get(post_id)
    try:
        fetched_title, fetched_text = fetch_url_text(url)
    except (HTTPError, URLError, TimeoutError, OSError):
        fetched_title, fetched_text = "", ""
    if fallback:
        fetched_title, fetched_text = fallback
    elif not fetched_title or not fetched_text:
        fetched_title, fetched_text = "", ""
    policy_title = clean_policy_title(fetched_title)
    policy_signal = policy_excerpt(fetched_text)
    money_signal = subsidy_highlight(fetched_text)
    title_variants = TITLE_VARIANTS_BY_POST_ID.get(post_id_from_url(url))
    article_title = title_variants[(index - 1) % len(title_variants)] if title_variants else make_article_title(planned_title, policy_title, index)
    article_title = normalize_article_title(str(article_title))
    if len(article_title) < 10:
        article_title = f"{article_title}补贴机会"[:TITLE_MAX_CHARS]
    title = policy_title or planned_title
    policy_subject = SUBJECT_BY_POST_ID.get(post_id_from_url(url)) or short_policy_subject(policy_title) or planned_title
    short_topic = re.split(r"[，,：:？?]", policy_subject)[0].strip()[:18] or "这类政策"
    policy_name = "这份政策原文"
    subsidy_sentence = f"原文中和补贴最相关的信号是：{money_signal}。" if money_signal else "如果原文里涉及补贴金额、资助比例或奖励条件，企业要优先把金额口径和材料口径核清楚。"
    original_signal_options = [
        f"从政策原文看，{policy_signal}。" if policy_signal else f"从政策原文看，企业要回到原文里的支持对象、项目条件、费用口径和材料要求来判断匹配度。",
        f"真正值得企业抓住的不是文件名称，而是里面的对象、项目、资金和材料边界。{subsidy_sentence}",
        f"如果把原文拆开看，企业至少要关注{policy_focus}，这些内容能不能落到自身项目上，决定了后续有没有申报价值。{subsidy_sentence}",
    ]
    opening_options = [
        f"{policy_name}来自{source}。{original_signal_options[0]}企业先别急着问能拿多少钱，而要核验适用范围、补贴价值、项目关联和材料基础。",
        f"{source}发布的相关政策，对{audience}来说值得重点关注。{original_signal_options[1]}只要这些要素能对应到企业现有项目，就有必要进入补贴评估。",
        f"看到这类政策后，企业要做的不是简单保存通知，而是判断它和自身业务的关系。{original_signal_options[2]}",
    ]
    match_options = [
        f"适合重点关注这类机会的主体包括{audience}。建议把{policy_focus}拆成几个判断题：是否符合企业主体，项目是否在规定周期内，费用是否能归集，成果是否可量化，是否存在重复申报限制。这样做能在申报前先判断成功概率。",
        f"从企业匹配角度看，{audience}不能只看政策名称，而要逐项核对{policy_focus}。如果项目投入、业务成果和政策要求之间缺少对应关系，即使材料很多也未必有效；反过来，平时留痕清楚的企业往往能更快形成申报方案。",
        f"这类政策最怕“看起来相关、申报时对不上”。{audience}应围绕{policy_focus}建立自查表，把企业已有条件、待补材料和风险点分开标注。先完成自查，再决定是否进入正式申报，会比临近截止时仓促准备更稳。",
        f"对{audience}来说，政策价值往往藏在细节里。企业要把{policy_focus}对应到真实业务场景，看看哪些投入已经发生、哪些成果可以证明、哪些资质还需要补强。判断清楚后，后续材料准备才不会偏题。",
        f"如果把政策当成一张清单来看，{audience}首先要确认{policy_focus}是否都能落到企业自身项目上。能落地的部分要马上标注证据来源，暂时缺失的部分要判断补齐成本，避免因为一个关键条件不满足而影响整篇申报材料。",
        f"这条机会对{audience}的启发在于，企业平时的运营动作要能和{policy_focus}形成对应关系。只有业务事实、财务数据和项目成果三者能相互印证，申报时才更容易说明政策匹配度。",
        f"判断是否申报时，{audience}可以先用{policy_focus}做一次内部访谈：项目负责人讲实施过程，财务说明费用路径，行政核对资质证照，管理层确认成果价值。多部门对齐后，申报方向会更清晰。",
        f"很多企业错过补贴，不是因为不符合政策，而是没有把{policy_focus}提前整理成可证明的材料。{audience}应把这些要点放入日常项目管理，后续遇到类似政策时才能快速响应。",
    ]
    material_options = [
        f"材料方面，优先整理{proof_materials}。同时检查主体名称、项目名称、合同金额、发票金额、付款路径、成果描述和申报口径是否一致。涉及评审、审计或现场核查时，还要准备项目背景、实施过程、投入明细、绩效成果和风险说明。",
        f"企业现在就可以搭建一份项目台账，把{proof_materials}按时间顺序归档。台账不是为了“好看”，而是为了让评审人员能看懂项目从立项、执行、付款到产生成效的全过程，减少后续反复补正。",
        f"如果企业已经开展相关项目，建议马上回看{proof_materials}是否齐全。常见问题包括合同名称和申报项目不一致、付款凭证缺少对应发票、成果资料只有截图没有说明、费用归集口径不清，这些都会影响补贴申报质量。",
        f"申报准备不要等通知截止前才开始。围绕{proof_materials}建立资料夹，并同步记录经办人、形成时间、金额来源和项目成果，后续无论是填申请书、做审计还是接受核查，都能节省大量沟通成本。",
        f"从资料颗粒度看，{proof_materials}不能只“有文件”，还要能讲清楚为什么发生、花在哪里、形成什么成果。建议企业在每份核心材料旁边补一段说明，后续写申报书时就能直接复用。",
        f"项目资料最好按“立项—执行—付款—验收—成效”五个阶段归档，{proof_materials}分别放入对应位置。这样做的好处是，一旦政策要求补充过程证明或绩效说明，企业能迅速找到依据。",
        f"企业可先把{proof_materials}做成一张缺口表，标明已有、待补、无法提供三种状态。对无法提供的证明，要尽早寻找替代材料或说明口径，不能等到系统提交前才临时处理。",
        f"对申报负责人来说，{proof_materials}还需要统一命名和版本。合同、票据、成果、照片、截图如果散落在不同人员电脑里，后续整理会非常低效，也容易出现口径不一致。",
    ]
    company_options = [
        f"深圳金赋的补贴平台可以先帮助{audience}做企业画像和资质评估，再把政策拆成申报条件、材料清单、关键节点和风险提醒。平台沉淀全国四级政府公开扶持政策数据，可按地区、行业、规模、资质、研发投入、知识产权、项目费用和时间窗口进行匹配。",
        f"深圳金赋做的不是简单转发政策，而是通过补贴平台帮企业判断“这条能不能申、现在缺什么、还有哪些政策能一起看”。对于{audience}，平台会把政策要求翻译成可执行清单，让负责人、财务、项目和行政团队知道各自要准备什么。",
        f"补贴平台的价值在于把分散政策变成企业自己的申报地图。深圳金赋可围绕{audience}的注册地、行业标签、资质基础、项目投入和材料成熟度，筛选出值得优先跟进的政策，并提示申报节奏和合规风险。",
        f"很多企业不是没有政策机会，而是不知道如何排序。深圳金赋补贴平台会结合{audience}的经营数据、项目阶段和证明材料，判断先做哪项补贴更合适，哪些政策适合储备，哪些材料需要提前补齐。",
        f"深圳金赋长期服务企业做政策匹配和申报规划，核心是让企业少走弯路。补贴平台会把{audience}可能涉及的区域政策、行业政策、资质政策和项目资金政策放在一起比对，帮助企业看清优先级。",
        f"对{audience}而言，补贴平台更像一套政策工作台：先录入企业基础信息，再形成政策推荐，再把材料缺口、申报节点和责任分工列出来。这样政策跟进不再只靠人工记忆，也不容易漏掉窗口。",
        f"深圳金赋关注的不只是单次申报结果，还包括企业后续能不能持续匹配政策。补贴平台会帮助{audience}沉淀资质、项目、费用和成果资料，下一次遇到类似政策时，可以更快判断是否具备申报基础。",
        f"如果企业内部缺少专门的政策团队，深圳金赋补贴平台可以先完成第一轮筛选：哪些政策适合{audience}，哪些只是看起来相关，哪些需要先做资质培育。企业再决定是否投入正式申报资源。",
    ]
    value_options = [
        f"围绕{short_topic}，企业还可以继续排查同区域、同产业、同项目阶段下的其他补贴，判断是否存在区级配套、市级专项、省级扶持或国家级资质培育机会。把日常投入沉淀成可申报项目，才是持续拿补贴的关键。",
        f"如果企业只盯单条政策，往往容易错过组合机会。以{short_topic}为入口，可以同步梳理研发、市场、人才、融资、合规和品牌等相关政策，形成一张年度补贴路线图，而不是零散碰运气。",
        f"真正高效的申报，不是每次临时找材料，而是把这类机会纳入企业年度经营计划。项目启动时就考虑政策口径，费用发生时就保留证据，成果形成时就准备说明，补贴申报会更从容。",
        f"从企业服务角度看，{short_topic}也是一次重新整理企业资产的机会：哪些投入能证明，哪些资质能加分，哪些项目还能延伸申报。补贴平台能帮助企业把这些信息沉淀下来，后续遇到新政策时快速复用。",
        f"{short_topic}不应只被当成一次通知，而应成为企业优化内部管理的提醒。凡是与政策相关的投入，都要形成预算、合同、票据、成果和复盘，这些资料未来可能同时服务多个补贴项目。",
        f"企业还可以借这次机会重新梳理年度预算：哪些投入已经发生，哪些投入即将发生，哪些成果需要补证明。只要项目管理更规范，政策机会出现时就不会因为资料缺口而被动。",
        f"对成长型企业来说，{short_topic}背后还有一个更重要的问题：企业是否已经形成持续申报能力。一次补贴可以解决短期资金压力，长期材料体系和政策路线图才会带来稳定收益。",
        f"把这类政策放进企业经营会议中讨论，也能帮助管理层看清政策与业务的关系。不是所有补贴都要申，但值得申的项目必须提前规划、提前留痕、提前分工。",
    ]
    next_step_options = [
        f"下一步，{audience}可以先把企业基础信息、近两年项目投入和已获资质导入补贴平台，由平台初筛政策适配度；再由内部负责人确认申报优先级，避免所有政策平均用力。这样既能保留机会，也能控制申报成本，把有限精力放在最有把握的项目上。",
        f"实际执行时，建议{audience}把政策事项分成“马上可申报、需要补材料、适合长期培育”三类。补贴平台生成的清单可以作为部门协作依据，减少老板、财务和项目团队之间的信息差。后续即使政策口径调整，也能快速定位受影响的材料和项目。",
        f"如果企业已经有相关投入，{audience}应尽快做一次材料盘点，把缺口列出来：缺合同就补协议，缺成果就补报告，缺数据就补统计。越早补齐，越容易赶上后续申报窗口，也能避免因为一个证明缺口影响整项补贴的推进。",
        f"对于计划新上项目的{audience}，也可以反过来用政策要求指导项目管理：立项时明确目标，执行时保存证据，付款时规范票据，结项时形成成果，这样项目天然更适合申报补贴，也能让经营投入、合规投入和市场投入都留下可复用的政策证据。",
        f"建议{audience}先做一次“政策—项目—材料”三列表：左边放政策条件，中间放企业对应项目，右边放现有证明。三列能够对应上的，优先推进；对应不上的，先判断是否值得补齐，而不是盲目准备全套材料。",
        f"企业内部可以指定一名政策负责人，把{audience}相关项目按月更新到补贴平台。只要新增资质、新增费用、新增成果，就及时刷新匹配结果，避免等到申报期才发现材料跨部门、数据找不到。",
        f"如果企业已经有多个项目同时推进，{audience}要特别注意不重复享受和费用边界。哪些发票只能用于一个项目，哪些成果可以作为辅助证明，哪些费用不能重复计算，都应在申报前先做标注。",
        f"对刚开始做政策管理的{audience}，不必一次追求所有补贴都覆盖。可以先选一两个匹配度高、材料成熟度高的项目练手，建立路径后，再逐步扩展到资质培育、项目资金和区级配套。",
    ]
    review_options = [
        f"同时，企业还应把相关机会放进年度补贴日历，标注预计申报时间、牵头部门、配合部门和关键材料负责人。只要政策一启动，就能按清单推进，而不是临时翻聊天记录找资料。",
        f"从管理层角度看，{short_topic}还可以作为一次内部体检：项目有没有预算，费用有没有凭证，成果有没有数据，资质有没有短板。把这些问题提前暴露出来，后续申报会更稳。",
        f"对{audience}而言，政策准备不是一次性动作，而是持续积累。每完成一个项目，都应同步沉淀合同、票据、成果和复盘，后续无论申报哪类补贴，都能少走弯路。",
        f"如果企业内部没有专人跟政策，这类机会很容易被忽略。建议把政策匹配、材料归档和申报提醒固化为月度动作，让补贴申报从偶然机会变成常规管理。",
        f"企业还要注意，政策申报不是把材料堆上去就结束。围绕{short_topic}，最好提前准备项目逻辑、资金逻辑和成果逻辑，让材料之间能相互解释，而不是各说各话。",
        f"在正式申报前，{audience}可以做一次模拟审查：材料是否齐全，金额是否一致，项目描述是否前后统一，证明是否能支撑政策要求。提前发现问题，比提交后补正更主动。",
        f"对外部政策变化保持敏感也很重要。围绕{short_topic}，企业可以持续关注同主管部门、同产业方向、同区域层级的后续通知，避免只看一次政策就停止跟进。",
        f"如果企业希望长期拿补贴，就要把{short_topic}相关事项变成内部管理动作：项目立项问政策，费用发生留凭证，成果验收做复盘，年度总结看下一轮申报。",
    ]
    service_options = [
        f"更重要的是，企业要把补贴工作从“有人提醒才看”变成“每月主动复盘”。深圳金赋可围绕{audience}建立政策跟踪、材料维护和节点提醒机制，让经营数据、项目资料和补贴机会保持同步。",
        f"从实际辅导经验看，很多申报问题都出在前期：项目命名不统一、付款凭证缺失、成果证明太弱、内部人员更换后资料断档。补贴平台可以帮助{audience}把这些风险提前暴露出来，减少临门一脚的返工。",
        f"企业也要避免只关注最高金额。适合自己的政策，往往取决于主体资质、材料成熟度和项目匹配度。深圳金赋会先帮{audience}判断申报性价比，再建议是否推进正式材料准备。",
        f"如果企业正在做年度预算或项目复盘，建议同步加入补贴视角。把{policy_focus}纳入项目管理指标，后续无论申报资金、资质认定还是区级配套，都更容易形成完整说明。",
        f"对老板和财务负责人来说，补贴规划还关系到资金效率。企业已经发生的研发、市场、设备、合规或运营投入，如果没有及时整理，就很难在政策窗口打开时转化为可申报资产。",
        f"深圳金赋强调先评估、再匹配、后申报。只有先把{audience}的业务事实、费用证据和资质基础看清楚，才能避免盲目申报，也能把真正值得争取的补贴项目排在前面。",
        f"每条政策背后都有主管部门关注的产业方向。企业如果能围绕{policy_focus}持续沉淀项目成果，下一次同类政策出现时，就不是从零开始，而是直接调用已经准备好的证明材料。",
        f"补贴不是临时福利，而是企业经营管理的一部分。对于{audience}，越早把项目、费用、成果和资料纳入补贴平台，越容易形成可复用的政策资产，也越容易把握后续申报机会。",
    ]
    closing_options = [
        f"如果企业想判断这类政策是否值得申报，并生成更贴合自身情况的补贴推荐清单，可关注「金赋补贴宝」，进入补贴平台，进行企业资质评估和政策匹配。",
        f"想知道{audience}现有项目能不能匹配这类机会，或者还缺哪些申报材料，可关注「金赋补贴宝」，进入补贴平台，先做一次企业资质评估。",
        f"近期有补贴申报、资质培育或项目资金规划需求的企业，可关注「金赋补贴宝」，进入补贴平台，查看适合自身情况的政策推荐。",
        f"如果{audience}不确定这类政策是否适合自己，建议先做一次资质评估和政策匹配。可关注「金赋补贴宝」，进入补贴平台，把企业资料转化为可执行的补贴清单。",
        f"企业也可以把这类机会作为年度补贴规划的起点。关注「金赋补贴宝」，进入补贴平台，先确认自身条件、材料缺口和可优先推进的政策方向。",
        f"不确定项目是否能申报，不建议只凭经验判断。关注「金赋补贴宝」，进入补贴平台，让系统先根据企业信息做匹配，再决定是否进入材料准备。",
        f"如果企业已经有项目投入，但不知道能否形成补贴申请，可关注「金赋补贴宝」，进入补贴平台，先完成资质评估，再对照推荐清单安排申报节奏。",
        f"政策机会不会一直停留在通知里，关键是企业能不能及时行动。关注「金赋补贴宝」，进入补贴平台，把相关信息转化为自己的补贴评估结果。",
    ]
    ad_hook_options = [
        f"这类补贴政策不是让企业背条文，而是帮企业找到拿补贴、拿贴息的入口。深圳金赋补贴平台先做匹配，再看项目和材料值不值得推进。",
        f"企业别错过身边的补贴政策。只要{proof_materials}能说明项目真实发生，就可以先让补贴平台测一测有没有机会拿补贴。",
        f"企业最关心的不是政策有多长，而是自己能不能拿补贴。围绕{short_topic}，深圳金赋会先帮企业看主体、项目、费用和材料，再判断是否值得进入申报准备。",
        f"想拿补贴、拿贴息，别只靠人工翻政策。把企业信息放进补贴平台，先看适配度，再安排材料和申报节奏。",
        f"深圳金赋补贴平台帮企业找补贴政策、测申报机会、看材料缺口，让老板先知道值不值得做。",
        f"如果企业正在做融资、研发、设备、市场或合规投入，别只看成本，也要看看能不能衔接补贴、奖励或贴息政策。补贴平台可以先帮企业把机会筛出来。",
        f"对企业来说，拿补贴不是碰运气，而是提前把项目和材料准备好。深圳金赋把政策匹配、资质评估和材料提醒串起来，让补贴机会更容易被发现。",
        f"有项目、有投入、有凭证，就别急着说自己不符合。先上补贴平台做评估，看看能不能申补贴、拿贴息或进入资质培育。",
        f"补贴政策不是离企业很远，它可能就在已有项目里。深圳金赋帮企业把政策、项目和证据对上，少走弯路。",
        f"重点不是复述文件，而是让企业行动起来：把项目放进补贴平台测一测，看看有没有补贴、贴息、奖励或配套资金线索。",
    ]

    extra_options = [
        f"补充一句更落地的话：围绕{short_topic}，{audience}可以把现有项目分成“马上评估、继续养项目、暂时不推进”三类。补贴平台会把企业基础、项目投入、资质条件和材料成熟度放在一起看，让政策机会不再只停留在收藏夹里。",
        f"很多补贴机会不是突然冒出来的，而是企业平时把{proof_materials}留完整后，窗口打开时自然能接上。深圳金赋更希望企业提前把资料变成可复用资产，而不是每次申报都从头找人、找票、找合同。",
        f"对企业负责人来说，{short_topic}真正要回答的是“哪些投入有机会转化为补贴”。如果项目事实、费用路径和成果证明能讲通，就值得进入评估；如果目前还缺证据，也能提前进入培育。",
        f"如果团队担心政策太多看不过来，可以先让补贴平台按区域、行业、资质和项目阶段筛一遍。系统先给出方向，企业再决定要不要投入申报精力，这样比人工逐条翻政策更省心。",
        f"尤其要提醒财务和项目负责人，围绕{source}的{short_topic}，{policy_focus}不能只停留在口头描述。合同、发票、付款、成果和数据最好能互相印证，后续无论写材料还是接受核查，都会更有底气。",
        f"换个角度看，{short_topic}也是一次企业资料整理机会。把平时零散的项目、费用、证书、照片和成果说明沉淀到补贴平台，后面遇到类似政策时，企业就不用再临时拼材料。",
        f"有些企业明明项目不错，却因为资料散、口径乱、负责人换了而错过机会。深圳金赋希望通过补贴平台把政策匹配和资料管理前置，让{audience}更早知道自己差在哪里、能争取什么。",
        f"如果要写进企业年度计划，{short_topic}不只是一个政策提醒，更是一条资金线索。把它和研发、设备、人才、市场、合规等投入放在一起看，往往能发现更多组合申报空间。",
        f"企业不用把这类政策读成公告，先弄清自己有没有项目、材料缺什么、是否值得评估，补贴平台正好可以把这些问题筛一遍。",
        f"换成企业能听懂的话，就是别让已经发生的投入躺在文件夹里。把项目、费用、成果和资质放进补贴平台，才有机会在政策窗口打开时快速响应。",
        f"有些机会现在未必马上申报，但可以先做储备。企业把{proof_materials}补齐后，后续遇到同类通知，就能少花时间解释项目来龙去脉。",
        f"对企业服务团队来说，{short_topic}也能变成一次有价值的提醒：帮助企业做政策体检，比单纯转发通知更有用。",
        f"如果企业以前申报过补贴，也可以借这次机会复盘旧材料。哪些资料可以复用，哪些口径要更新，哪些项目还能衔接新的政策方向，都值得重新整理。",
        f"从长期服务看，补贴工作越早进入日常管理越好。每月更新一次项目和材料，往往比申报期突击整理更稳，也更容易发现组合申报机会。",
        f"这类政策还可以用来提醒企业做预算前置：未来准备投入的设备、研发、市场或合规事项，能否提前按政策口径留证据，决定后续能不能申报。",
        f"说到底，补贴平台不是替企业制造项目，而是帮企业发现已有项目里的政策价值。只要真实业务和证明材料足够清楚，政策机会就更容易被看见。",
    ]
    padding_options = [
        f"再补一层实际建议：这次从{source}看到的{short_topic}，企业可以先让补贴平台做一次轻量匹配，把可评估项目、待培育条件和暂不适合事项分开，后续推进会更清楚。",
        f"如果团队担心政策太多看不过来，可以先按地区、行业、资质和项目阶段筛一遍。系统给出初步方向后，企业再决定要不要投入申报精力，比人工逐条翻政策更省心。",
        f"尤其要提醒财务和项目负责人，围绕{source}的{short_topic}，{policy_focus}不能只停留在口头描述。合同、发票、付款、成果和数据最好能互相印证，后续无论写材料还是接受核查，都会更有底气。",
        f"换个角度看，{short_topic}也是一次企业资料整理机会。把平时零散的项目、费用、证书、照片和成果说明沉淀到补贴平台，后面遇到类似政策时，就不用再临时拼材料。",
        f"如果企业已有项目但不确定是否匹配，可以先做预评估。预评估不等于马上申报，而是先判断对象、费用、时间、成果和证明材料是否值得继续推进。",
        f"对企业老板来说，这类政策最有用的地方，是帮助判断哪些经营投入可能形成资金回流。把投入和政策对应起来，补贴申报才不会变成临时碰运气。",
        f"政策不是让企业背条文，而是提醒企业把项目证据留好，把能争取的补贴机会先看清楚。",
        f"很多企业不是没机会，而是资料太散。把{proof_materials}提前放进统一台账，后续申报时就能快速找到证据，不会因为跨部门沟通浪费窗口期。",
        f"项目还没完全成熟也没关系，先把缺口列出来。缺成果就补案例，缺费用说明就整理台账，缺资质就进入培育，这样下一次政策窗口出现时更从容。",
        f"这类政策也适合和其他补贴一起看。企业可以同步排查同区域、同产业、同项目阶段下的配套资金，避免只盯单条通知而错过组合机会。",
        f"企业真正关心的通常不是文件名字，而是自己能不能用。把政策转成评估动作，会比复述条款更容易形成内部判断。",
        f"补贴平台的优势是先把复杂政策拆成企业看得懂的判断项：主体、项目、费用、材料、时间和风险。判断清楚后，是否推进就更容易决定。",
    ]
    variant = (index - 1)
    STYLE_VARIATION_COUNT = 128
    has_specific_plan = post_id_from_url(url) in PLAN_BY_POST_ID
    style = variant % STYLE_VARIATION_COUNT
    if not has_specific_plan:
        style = 16 + (variant % (STYLE_VARIATION_COUNT - 16))
    if style == 0:
        paragraphs = [
            f"先看企业最关心的数字：入驻南山人力资源服务产业园的人才服务机构，前两年可按实际支付租金70%申请补贴，每年最高100万元；第三年至第五年仍可按50%申请，每年最高70万元。对正在园区经营的机构来说，房租不是小开支，完全值得先测一轮。",
            f"原文里的关键口径很清楚：{policy_focus}。尤其是70%和50%两档比例、100万元和70万元上限、12个月一个年度、不含税租金和付款时间，都会影响最终可评估金额。",
            f"深圳金赋成立于2017年，长期为企业做补贴申报政策匹配和材料管理。补贴平台会先把机构入驻状态、实际经营地、租赁合同、付款凭证和租金归属期放在一起看，避免只凭感觉判断。",
            f"企业可以先准备{proof_materials}，不用一开始就写长材料，先把能证明入驻事实、经营事实和租金真实发生的资料集中起来。",
            f"如果初筛发现符合方向，再进一步测算前两年70%补贴和后续50%补贴空间；如果资料暂时不完整，也可以进入培育清单，后续补齐票据、证明和承诺材料后继续匹配。",
            closing_options[(variant + 8) % len(closing_options)],
        ]
    elif style == 1:
        paragraphs = [
            f"南山的人才服务机构如果正在为园区租金压力头疼，这项房租补贴就很值得关注。政策不是泛泛支持服务业，而是锁定人力资源服务产业园入驻机构，并把补贴年度、比例和上限写得很具体。",
            f"简单说，前两年按实际支付租金70%补，最高100万元；第三年至第五年按50%补，最高70万元。补贴从首次申请起连续计算，以12个月为一个年度，每年申报一次。",
            f"这时候不要只问“能拿多少”，而要先问三件事：申请补贴时间段是否实际经营在南山园区，租金归属期和付款时间是否符合，是否存在同类租赁补贴重复申报风险。",
            f"补贴平台可以把这些问题变成一张匹配表。深圳金赋会结合{proof_materials}，帮机构先看申报基础，再判断是否需要补充不含税租金明细、入驻证明或未重复申报承诺。",
            f"对成长型人才服务机构来说，房租补贴不只是省成本，更是把园区经营投入纳入年度补贴规划。越早把租金资料放进平台，后续匹配服务业专项资金、稳商政策和区级配套时就越顺。",
            service_options[(variant + 2) % len(service_options)],
        ]
    elif style == 2:
        paragraphs = [
            f"把这项政策换成财务语言，就是“园区租金支出有没有机会形成资金回流”。南山区人力资源服务产业园房租补贴属于核准类项目，采取无偿资助和事后补贴制，材料口径一定要站得住。",
            f"原文特别强调租金不含税，并以租金实际归属期为准，付款时间需在项目开通前。这个点很关键，企业不能只看付款总额，还要把税额、归属期和付款凭证核清楚。",
            f"机构可以先把租赁合同、租金发票、付款凭证、不含税租金明细、入驻证明和经营证明拉出来，按12个月年度做一份房租补贴台账。台账越清楚，70%或50%的补贴比例越容易测算。",
            f"深圳金赋补贴平台适合做前置测算：机构把基础信息录入后，平台先判断是否属于园区入驻机构、是否在补贴时间段实际经营于南山，再看材料缺口。",
            f"如果机构处在首次申请后的第一年或第二年，就要重点关注最高100万元上限；如果已经进入第三到第五年，也不要忽略最高70万元的持续补贴空间。",
            closing_options[(variant + 5) % len(closing_options)],
        ]
    elif style == 3:
        paragraphs = [
            f"这条政策对人才服务机构负责人很直接：园区已经入驻，租金也在持续支付，是否有机会拿回一部分成本？对于拥有核心产品、成长性好、竞争力强的人才服务机构，最高100万元的年度补贴值得进入经营会议讨论。",
            f"但补贴不是只看“在园区”，还要看实际经营地、入驻机构身份、租金归属期、付款时间和不重复申报。辖区同类租赁补贴、前海同类扶持政策，都不能重复申报。",
            f"机构如果正在扩大顾问团队、打造招聘交付产品、做人才测评系统或承接区域人才服务项目，建议同步做政策评估。核心产品介绍、成长性和知名度证明，也会影响材料完整度。",
            f"补贴平台会把政策条件和机构现状对应起来：哪些租金可纳入，哪些月份归属期符合，哪些票据需要补齐，哪些重复申报风险要提前排除。",
            f"深圳金赋服务企业拿补贴，最看重的是“先测再准备”。符合方向就继续完善材料，不符合也能知道差在哪里，避免把普通房租支出盲目整理成申报材料。",
            value_options[(variant + 1) % len(value_options)],
        ]
    elif style == 4:
        paragraphs = [
            f"如果人才服务机构今年想降本，别只盯业务开支，园区房租也可能有补贴线索。南山这项专项资金对入驻人力资源服务产业园的机构给出支持，前两年最高100万元，后续三年最高70万元。",
            f"最关键的适用范围包括：申请补贴时间段实际经营地在南山区的人力资源服务产业园入驻机构，含分支机构；同时要守法经营、诚实守信、履行数据申报义务，并有规范财务管理制度。",
            f"这里有两个容易忽略的点：一是补贴租金按不含税口径核算；二是不得和辖区其他同类租赁补贴、前海同类扶持政策重复申报。",
            f"深圳金赋补贴平台会先做“能不能匹配”的判断，再提示材料怎么补。机构上传{proof_materials}后，可以更快看到自身条件与政策要求之间的距离。",
            f"对财务来说，这是一次规范租金台账的机会；对管理层来说，这是一次把固定成本转化为补贴机会的机会。别等申报窗口临近才整理，提前评估更稳。",
            closing_options[(variant + 3) % len(closing_options)],
        ]
    elif style == 5:
        paragraphs = [
            f"很多机构会觉得：我们只是正常入驻园区、正常交租，和补贴有什么关系？这项政策给了一个明确答案——只要属于南山人力资源服务产业园入驻机构，租金真实发生、材料符合，就可能进入房租补贴评估。",
            f"补贴金额不是一刀切，而是和入驻年限、实际支付租金、不含税金额和年度上限相关。第一年和第二年最高100万元，第三年到第五年最高70万元，补贴比例分别为70%和50%。",
            f"建议机构先做一张“园区租金补贴小账本”：租赁合同、月租金、发票税额、付款凭证、租金归属期、首次申请时间、是否连续计算，都放进去。",
            f"补贴平台可以把这张小账本变成政策匹配结果。深圳金赋会帮助机构判断当前处于哪一个补贴年度，也会提醒哪些租金期间、票据和承诺材料需要单独整理。",
            f"如果暂时缺少核心产品、成长性或知名度证明，也不要急着放弃。机构可以先进入政策培育，后续补充服务案例、产品资料、行业荣誉或经营数据后，再重新测算。",
            service_options[(variant + 5) % len(service_options)],
        ]
    elif style == 6:
        paragraphs = [
            f"这项南山人才服务园房租补贴，适合用来做一次机构自查。自查不用复杂，先看四个词：入驻、租金、年度、排重。",
            f"入驻：申请补贴时间段实际经营地是否在南山区人力资源服务产业园。租金：合同、发票、付款凭证和不含税明细是否能对应实际归属期。",
            f"年度：补贴从首次申请起连续计算，以12个月为一个年度，每年申报一次。排重：辖区同类租赁补贴和前海同类扶持政策不能重复申报。",
            f"四项能对上，再看补贴空间：前两年70%比例、每年最高100万元，第三年至第五年50%比例、每年最高70万元。",
            f"深圳金赋补贴平台可以把自查结果保存下来，形成机构自己的园区补贴档案。以后遇到租金补贴、重点服务业专项资金、稳商扶持等同类政策，系统也能更快提示。",
            closing_options[(variant + 6) % len(closing_options)],
        ]
    elif style == 7:
        paragraphs = [
            f"对人才服务机构来说，园区租金不只是成本，也可能是一项可管理的政策资产。入驻以后，如果没有同步留好合同、票据、付款和经营证明，后面想申房租补贴就会很被动。",
            f"这项专项资金采用核准类、无偿资助、事后补贴制，说明机构申报时更看重事实和材料是否清楚。受资助项目无需验收，不代表材料可以粗略。",
            f"原文中的重点包括70%补贴比例、前两年最高100万元、第三到第五年50%补贴、每年最高70万元、12个月一个年度、不含税租金和不得重复申报。",
            f"深圳金赋建议机构把房租补贴当成年度专项资金规划的一部分：每月归集租金付款，每年更新入驻证明和经营资料，申报前再复盘是否存在同类政策重复享受风险。",
            f"补贴平台会根据机构资料动态匹配政策，帮助老板、财务和行政看到同一套判断依据，减少“园区证明找不到、发票税额没剔除、重复申报没人确认”的情况。",
            value_options[(variant + 2) % len(value_options)],
        ]
    elif style == 8:
        paragraphs = [
            f"先说一句实在的：园区房租已经交了，如果符合政策条件，就别让它只停留在费用表里。南山人力资源服务产业园入驻机构的租金支出，有机会通过专项资金做补贴评估。",
            f"政策支持对象并不泛泛，而是锁定拥有核心产品、成长性好、竞争力强、全球性或国内知名的人才服务机构，同时要求申请补贴时间段实际经营地在南山区园区。",
            f"机构最好现在就把{proof_materials}集中起来，让补贴平台先看一遍。资料齐不齐、口径对不对、补贴年度能不能测算，都会影响后续推进。",
            f"尤其是租金实际归属期、付款时间和不含税金额，别凭印象。一个影响补贴期间，一个影响补贴基数，都关系到机构能评估出的补贴空间。",
            f"深圳金赋做补贴平台，不是让机构追每一条政策，而是帮助机构找到更可能转化为补贴、贴息或奖励的机会。房租这类高频成本，当然值得优先放进清单。",
            closing_options[(variant + 1) % len(closing_options)],
        ]
    elif style == 9:
        paragraphs = [
            f"给南山人才服务机构一个提醒：如果已经入驻人力资源服务产业园并持续支付租金，这项房租补贴政策可以尽快做匹配。前两年最高100万元、后三年最高70万元，不适合只靠人工记忆来判断。",
            f"机构先看自己在哪一段：第一年和第二年按实际支付租金70%测算，每年最高100万元；第三年到第五年按50%测算，每年最高70万元。",
            f"测算之外，还要看材料。入驻证明、租赁合同、租金发票、付款凭证、南山经营证明、数据申报证明和未重复申报承诺如果分散在不同部门，就要尽快归集。",
            f"补贴平台可以把这些信息变成机构自己的政策画像：哪些条件已满足，哪些材料待补，预计该优先看哪类专项资金。深圳金赋再结合机构情况给出更清晰的申报判断。",
            f"这类补贴最适合提前准备。等通知出来才翻合同、找票据、核归属期，往往会耽误节奏；现在把资料整理好，后续有窗口就能更快响应。",
            service_options[(variant + 7) % len(service_options)],
        ]
    elif style == 10:
        paragraphs = [
            f"老板一句话：这项政策和公司有什么关系？项目负责人可能说项目相关，财务可能说票据要再查，行政可能说资质还要确认。围绕{short_topic}，补贴平台就是把这些回答放到同一张图里。",
            f"从原文提炼，企业要重点看{policy_focus}。{subsidy_sentence}这些信息决定了企业是马上评估，还是先继续培育。",
            f"深圳金赋会先帮企业把“能不能申”的问题拆开：主体是否匹配、项目是否真实、费用是否合规、成果是否可证明、材料是否够完整。",
            f"如果{audience}已经有类似项目，可以先把{proof_materials}交给平台做匹配；如果目前项目还在推进中，也可以提前按政策口径留痕。",
            f"老板、财务和项目负责人都可以一起看，因为补贴不是某一个部门的事。{review_options[(variant + 2) % len(review_options)]}",
            f"有了补贴平台，企业就不用靠人工记忆追政策。围绕{short_topic}这个主题，{value_options[(variant + 5) % len(value_options)]}",
            closing_options[(variant + 1) % len(closing_options)],
        ]
    elif style == 11:
        paragraphs = [
            f"如果把企业补贴申报比作一场备考，{short_topic}就是一道新题。题目难不难，不能只看标题，要看企业平时有没有把项目、费用和成果准备好。",
            f"这道题的考点大概落在{policy_focus}。{opening_options[(variant + 2) % len(opening_options)]}",
            f"深圳金赋补贴平台适合做“预判”：哪些材料能直接用，哪些材料还缺说明，哪些项目虽然相关但暂时不建议投入太多精力。",
            f"{proof_materials}就是企业的答题材料。材料越能说明真实投入和实际成效，越有机会把政策机会变成申报项目。",
            f"当然，不是所有企业都要自己研究政策。对于{audience}，更高效的做法是先把企业信息放进补贴平台，让系统给出匹配结果和材料建议。",
            extra_options[(variant + 3) % len(extra_options)],
            closing_options[(variant + 4) % len(closing_options)],
        ]
    elif style == 12:
        paragraphs = [
            f"有些政策看起来严肃，其实落到企业就是一句话：{short_topic}提醒企业把已经做过的项目、正在发生的投入、未来要补的资质，都从补贴角度重新看一遍。",
            f"从政策原文看，企业应关注{policy_focus}。如果原文中出现奖励、补助、资助比例或金额上限，就要进一步核对自己项目是否在支持范围内。",
            f"深圳金赋的补贴平台不是简单展示政策，而是帮企业做匹配。{company_options[(variant + 2) % len(company_options)]}",
            f"对{audience}来说，最怕的是“知道有政策，但不知道自己能不能用”。平台会把{proof_materials}和政策条件对应起来，让企业先看到差距。",
            f"差距不是坏事，提前知道就能提前补。比如成果证明弱，就补案例；费用归集乱，就整理台账；项目口径不清，就统一说明。",
            f"所以要提醒企业别等申报截止才行动，而是把政策匹配变成日常经营动作。{service_options[(variant + 3) % len(service_options)]}",
            closing_options[(variant + 5) % len(closing_options)],
        ]
    elif style == 13:
        paragraphs = [
            f"给{audience}一个简单判断：如果今年有项目投入、有资质建设、有市场拓展或合规成本，就别忽略{short_topic}这类政策信号。它不一定马上对应一笔补贴，但可能对应下一轮申报准备。",
            f"深圳金赋成立以来一直服务企业做补贴申报，最深的感受是：很多企业不是不符合条件，而是没有提前整理材料。{original_signal_options[variant % len(original_signal_options)]}",
            f"围绕{policy_focus}，企业可以先做一次轻量盘点。哪些项目已经完成，哪些费用能够归集，哪些成果有客户或数据支撑，哪些资质还需要补强。",
            f"如果盘点后发现{proof_materials}比较完整，就可以进入政策匹配；如果还不完整，也可以先放入培育清单，后续持续补资料。",
            f"补贴平台会把企业信息沉淀下来，后面遇到同类政策时，系统可以更快提醒企业。{company_options[(variant + 6) % len(company_options)]}",
            extra_options[(variant + 4) % len(extra_options)],
            closing_options[(variant + 7) % len(closing_options)],
        ]
    elif style == 14:
        paragraphs = [
            f"从企业拿补贴的角度看，{short_topic}最值得企业关注的不是新闻热度，而是能否拆成可操作的补贴线索。{source}发布的信息里，企业要重点看对象、项目、资金和材料边界。",
            f"如果{audience}涉及{policy_focus}，建议先做一轮快速筛选。筛选的目的不是马上申报，而是判断这条线索是否值得继续跟。",
            f"深圳金赋补贴平台会把政策线索和企业情况放在一起比对：注册地、行业、资质、项目投入、证明材料、历史申报情况，都会影响最终匹配结果。",
            f"材料方面，{proof_materials}要尽量围绕项目形成闭环。评估时最怕资料零散，明明有投入，却讲不清楚项目和政策之间的关系。",
            f"如果原文提到资金支持，企业还要重点看是否存在补贴上限、比例、对象范围和不重复享受要求。金额不是唯一重点，适配度才是能否推进的前提。",
            f"这也是深圳金赋强调补贴平台的原因：先把{short_topic}相关机会筛出来，再把材料管起来，最后再决定是否推进申报。{service_options[(variant + 6) % len(service_options)]}",
            closing_options[(variant + 2) % len(closing_options)],
        ]
    elif style == 15:
        paragraphs = [
            f"给企业一个直接提醒：企业别只忙着做项目，也要记得看看项目有没有政策价值。深圳金赋补贴平台，就是帮企业把这些价值找出来。",
            f"这类政策背后的关键词是{policy_focus}。{subsidy_sentence}企业不用把所有条款都背下来，但要知道哪些条件和自己有关。",
            f"对{audience}来说，最实在的动作是把现有项目拿出来做匹配：项目做了多久、费用花在哪里、成果怎么证明、资料是否齐全。",
            f"如果{proof_materials}能对应上政策口径，就有机会继续推进；如果对应不上，也能提前知道短板在哪里。别等到别人开始申报了，自己才发现资料还散在各个部门。",
            f"深圳金赋不是让企业追每一条政策，而是帮企业筛出更可能转化为补贴的机会。{company_options[(variant + 1) % len(company_options)]}",
            f"所以，可以直接提醒企业：政策不是离企业很远的文件，它可能就藏在企业已经发生的投入里。{value_options[(variant + 2) % len(value_options)]}",
            closing_options[(variant + 3) % len(closing_options)],
        ]
    else:
        composed_openings = [
            f"这篇换个说法：{short_topic}不是一条冷冰冰的通知，而是企业重新审视项目投入的机会。{original_signal_options[variant % len(original_signal_options)]}",
            f"如果把{short_topic}发给企业负责人，可以先讲一句大白话：政策能不能用，最终要看项目、费用和证据是否站得住。",
            f"很多企业看到{short_topic}会先收藏，但真正有价值的动作，是把它和现有项目放在一起评估。{opening_options[(variant + 1) % len(opening_options)]}",
            f"换到企业日常管理里看，{short_topic}适合做一次轻提醒：别等申报开始才找资料，平时的项目记录就是后续拿补贴的基础。",
            f"给团队开会时，可以把{short_topic}当成一个切入点：今年做过哪些项目，哪些费用能证明，哪些成果能量化。",
            f"{source}释放的这类政策信号，最适合提醒{audience}先做政策匹配，而不是盲目准备全套申报材料。",
            f"说得直接点，{short_topic}能不能变成企业机会，不取决于标题好不好看，而取决于{policy_focus}能否对应到企业事实。",
            f"提醒可以更直接：你们今年如果有相关投入，建议先别错过{short_topic}这条线索。",
        ]
        composed_angles = [
            f"企业要看的不是文件篇幅，而是{policy_focus}。这些要素能对应到真实项目，才有继续评估的必要。",
            f"围绕{short_topic}，如果原文里提到补贴、奖励、资助比例或资金安排，企业要把金额口径和费用边界单独标出来。{subsidy_sentence}",
            f"对{audience}而言，最容易被忽略的是资料成熟度。{proof_materials}越完整，后续判断越快。",
            f"政策往往不会替企业把路铺好，企业要主动把业务事实、投入金额、成果证明和政策要求连起来。",
            f"同一条政策，对不同企业的价值完全不一样。有项目、有费用、有证明的企业，才更值得进入下一轮评估。",
            f"如果企业暂时不满足条件，也不是没有意义。把缺口记下来，后续做资质培育、项目规划和费用留痕，下一批机会可能就接得上。",
            f"这类政策也适合做横向排查：同区域、同产业、同项目类型下，是否还有区级配套、市级专项或省级资金可以一起看。",
            f"别只问最高补贴金额，企业更要问自己能不能证明投入、能不能说明成果、能不能通过审核口径。",
        ]
        composed_company = [
            f"深圳金赋补贴平台会围绕{short_topic}，先把企业信息、行业标签、项目投入和材料状态放在一起看，帮企业判断哪些政策值得优先推进。",
            f"补贴平台的价值，是把分散政策变成企业自己的机会清单，让老板、财务、项目负责人看到同一套判断依据。",
            f"深圳金赋更关注申报前的判断：先看匹配度，再看材料缺口，最后再决定是否投入正式申报。",
            f"对于没有专门政策团队的企业，补贴平台可以先做一轮筛选，把可能适合的政策和暂时不建议推进的项目分开。",
            f"深圳金赋会把政策匹配和材料管理结合起来，帮助企业把合同、票据、成果、资质和复盘资料沉淀成可复用资产。",
            f"补贴平台不是让企业追所有政策，而是把真正可能转化为补贴的机会挑出来，再提示材料补强方向。",
            f"深圳金赋做这件事的核心，是让企业少靠经验猜测，多用数据和材料判断申报价值。",
            f"企业把基础信息放进补贴平台后，可以持续更新项目、资质和费用变化，让后续政策匹配更及时。",
        ]
        composed_actions = [
            f"建议企业把{proof_materials}先按项目归档，资料不必一开始完美，但要能看出项目发生、费用流向和成果形成。",
            f"如果企业近期刚完成相关项目，可以趁现在做一次复盘：投入是否清楚，成果是否可量化，材料是否能支持政策口径。",
            f"如果项目还在推进中，也可以提前按{policy_focus}留痕，避免后面为了补材料反复找人确认。",
            f"企业可以把这条政策放进年度补贴规划里，与研发、设备、市场、人才、合规等投入一起排优先级。",
            f"财务和项目团队最好提前统一口径，项目名称、合同金额、付款记录、成果说明不要各说各话。",
            f"如果目前资料散在多个部门，先集中到补贴平台做一次盘点，比临近截止时临时拼材料更稳。",
            f"对于金额较大或周期较长的项目，企业还要关注不重复享受、费用边界和绩效说明，避免后续审核时被动解释。",
            f"把这条政策当作一次提醒也很好：以后每做一个项目，都同步留下合同、发票、照片、数据和总结。",
        ]
        layout = (style - 16) % 16
        if layout == 0:
            paragraphs = [
                composed_openings[variant % len(composed_openings)],
                composed_angles[(variant + 1) % len(composed_angles)],
                composed_company[(variant + 2) % len(composed_company)],
                composed_actions[(variant + 3) % len(composed_actions)],
                extra_options[(variant + 4) % len(extra_options)],
                closing_options[(variant + 5) % len(closing_options)],
            ]
        elif layout == 1:
            paragraphs = [
                f"企业经常会问：{short_topic}和我有什么关系？答案不在标题里，而在企业是否符合对象、项目、费用和材料要求。",
                composed_angles[(variant + 2) % len(composed_angles)],
                composed_actions[(variant + 4) % len(composed_actions)],
                composed_company[(variant + 6) % len(composed_company)],
                f"所以，先评估，再准备，别一上来就陷入复杂流程。{service_options[(variant + 1) % len(service_options)]}",
                closing_options[(variant + 2) % len(closing_options)],
            ]
        elif layout == 2:
            paragraphs = [
                f"从财务视角看，{short_topic}真正重要的是费用能不能解释清楚。政策资金最终看的是证据，不是企业口头描述。",
                composed_openings[(variant + 3) % len(composed_openings)],
                f"围绕{policy_focus}，企业要把费用、合同、成果和责任部门对应起来。{material_options[(variant + 2) % len(material_options)]}",
                composed_company[(variant + 5) % len(composed_company)],
                composed_actions[(variant + 7) % len(composed_actions)],
                extra_options[(variant + 1) % len(extra_options)],
                closing_options[(variant + 3) % len(closing_options)],
            ]
        elif layout == 3:
            paragraphs = [
                f"从企业的日常投入说起，项目每天都在做，但不是每笔投入都会自动变成补贴机会。",
                f"深圳金赋想提醒{audience}，真正要留意的是{policy_focus}。{subsidy_sentence}",
                composed_actions[(variant + 1) % len(composed_actions)],
                composed_company[(variant + 3) % len(composed_company)],
                f"这类政策不一定要马上冲刺，但一定值得进入企业资料库。后续同类政策再出现时，企业就不用从零开始。",
                closing_options[(variant + 4) % len(closing_options)],
            ]
        elif layout == 4:
            paragraphs = [
                f"给老板看的版本可以更短更直接：{short_topic}出现后，先别问能拿多少，先问公司有没有对应项目。",
                f"给财务看的重点是：{proof_materials}是否完整，金额和项目口径是否一致。",
                f"给项目负责人看的重点是：{policy_focus}能否用真实过程和成果说明清楚。",
                composed_company[(variant + 4) % len(composed_company)],
                f"三个角色对齐后，{short_topic}相关评估才不会变成某个人单打独斗。{value_options[(variant + 6) % len(value_options)]}",
                extra_options[(variant + 2) % len(extra_options)],
                closing_options[(variant + 6) % len(closing_options)],
            ]
        elif layout == 5:
            paragraphs = [
                f"可以先用“补贴体检”的思路来判断。{audience}看到{short_topic}后，先把企业主体、项目投入、材料证据和申报价值做一次检查。",
                composed_angles[(variant + 5) % len(composed_angles)],
                f"体检结果如果显示项目成熟，就进入政策匹配；如果资料不足，就先补台账、补成果、补费用说明。",
                composed_company[(variant + 1) % len(composed_company)],
                f"这样比直接堆申报流程更有用，因为企业先需要知道自己有没有机会。{review_options[(variant + 5) % len(review_options)]}",
                closing_options[(variant + 7) % len(closing_options)],
            ]
        elif layout == 6:
            paragraphs = [
                f"有些政策适合做成交付清单，有些更适合做成经营提醒。{short_topic}属于后者：它提醒企业把项目和资金机会连接起来。",
                composed_openings[(variant + 5) % len(composed_openings)],
                composed_angles[(variant + 6) % len(composed_angles)],
                composed_company[(variant + 7) % len(composed_company)],
                f"如果企业已经有相关投入，就不要只停留在转发层面。{next_step_options[(variant + 2) % len(next_step_options)]}",
                closing_options[variant % len(closing_options)],
            ]
        elif layout == 7:
            paragraphs = [
                f"换个更直白的说法：政策不是离企业很远的文件，很多时候它就藏在企业已经发生的项目、费用和成果里。{short_topic}也是如此。",
                composed_angles[variant % len(composed_angles)],
                f"深圳金赋补贴平台要做的，就是帮企业把这些线索捞出来。{composed_company[(variant + 2) % len(composed_company)]}",
                composed_actions[(variant + 4) % len(composed_actions)],
                f"如果企业觉得{short_topic}这类政策太多、太杂、太难判断，先做一次平台匹配就会清楚很多。{extra_options[(variant + 6) % len(extra_options)]}",
                closing_options[(variant + 1) % len(closing_options)],
            ]
        elif layout == 8:
            paragraphs = [
                f"企业先抓住一个痛点：投入不少，但不知道哪些能对应政策资金。{short_topic}正好适合拿来做一次项目匹配。",
                f"围绕{policy_focus}，先别急着写长篇材料，而是把企业现有项目和费用做一次匹配。",
                composed_company[(variant + 1) % len(composed_company)],
                f"如果{proof_materials}已经比较完整，就可以继续评估；如果还缺证据，也能先进入培育清单。",
                padding_options[(variant + 2) % len(padding_options)],
                closing_options[(variant + 3) % len(closing_options)],
            ]
        elif layout == 9:
            paragraphs = [
                f"老板可以先记住一点：看到{short_topic}，先判断公司今年有没有相关投入，而不是把政策转给行政就结束。",
                composed_angles[(variant + 3) % len(composed_angles)],
                f"财务要看票据和费用，项目负责人要看过程和成果，管理层要看值不值得推进。",
                composed_company[(variant + 4) % len(composed_company)],
                composed_actions[(variant + 5) % len(composed_actions)],
                closing_options[(variant + 6) % len(closing_options)],
            ]
        elif layout == 10:
            paragraphs = [
                f"有些企业项目做完后，才发现{short_topic}相关政策已经发布，材料却还散在不同部门。",
                f"类似情况并不少见。{audience}平时如果没有建立材料台账，政策窗口打开时就容易手忙脚乱。",
                f"深圳金赋补贴平台会先看{policy_focus}和企业项目是否对应，再提示{proof_materials}是否足够支撑申报判断。",
                f"如果政策涉及补贴金额或奖励条件，企业更要把费用边界、投入周期和证明强度核清楚。",
                padding_options[(variant + 4) % len(padding_options)],
                closing_options[(variant + 7) % len(closing_options)],
            ]
        elif layout == 11:
            paragraphs = [
                f"用一句话概括：{short_topic}不是让企业多存一份文件，而是提醒企业把项目和补贴机会连起来。",
                composed_openings[(variant + 2) % len(composed_openings)],
                f"对{audience}来说，先把{proof_materials}整理出来，比直接研究复杂条款更有效。",
                composed_company[(variant + 6) % len(composed_company)],
                f"后续如果发现匹配度高，再进入材料深化；如果匹配度一般，也能知道下一步要补什么。",
                closing_options[variant % len(closing_options)],
            ]
        elif layout == 12:
            paragraphs = [
                f"市场、财务、项目和行政都要知道，{short_topic}背后看的不是一个部门的材料。",
                f"市场能提供客户和传播成果，项目能提供过程资料，财务能提供费用路径，行政能核对资质证照。",
                f"把这些信息放进补贴平台，深圳金赋才能更准确地判断{policy_focus}是否能对应企业实际。",
                composed_actions[(variant + 6) % len(composed_actions)],
                padding_options[(variant + 7) % len(padding_options)],
                closing_options[(variant + 2) % len(closing_options)],
            ]
        elif layout == 13:
            paragraphs = [
                f"别浪费已经发生的投入。{short_topic}就是一次提醒：投入要留下证据，证据才可能变成申报基础。",
                composed_angles[(variant + 4) % len(composed_angles)],
                f"深圳金赋不是让企业追热点，而是帮企业把政策要求和真实业务对上。{composed_company[(variant + 3) % len(composed_company)]}",
                f"围绕{proof_materials}，企业可以先做资料体检，看看哪些已经能用，哪些还需要补说明。",
                padding_options[(variant + 8) % len(padding_options)],
                closing_options[(variant + 5) % len(closing_options)],
            ]
        elif layout == 14:
            paragraphs = [
                f"政策来了，不代表补贴自动到账；项目、费用、成果和材料都对得上，才有继续评估的价值。",
                f"{short_topic}相关机会，建议{audience}重点看{policy_focus}。",
                composed_company[(variant + 5) % len(composed_company)],
                f"如果企业已经有相关投入，可以把资料先放进补贴平台做匹配；如果没有，也可以作为后续项目规划参考。",
                f"企业不用先研究所有细节，可以先把机会筛出来，再决定是否继续推进。",
                closing_options[(variant + 4) % len(closing_options)],
            ]
        else:
            paragraphs = [
                f"从年度规划看，{short_topic}可以成为企业补贴地图上的一个新节点。它提醒企业把政策、项目和材料放在一起管理。",
                f"围绕{policy_focus}，企业可以同步看现有项目、计划投入和已经取得的成果。",
                f"深圳金赋补贴平台会帮助企业把这些信息沉淀下来，形成可持续更新的政策资产库。",
                composed_actions[(variant + 3) % len(composed_actions)],
                padding_options[(variant + 9) % len(padding_options)],
                closing_options[(variant + 6) % len(closing_options)],
            ]
    if not any(keyword in paragraph for paragraph in paragraphs for keyword in ("拿补贴", "拿贴息", "补贴政策")):
        paragraphs.insert(-1, ad_hook_options[variant % len(ad_hook_options)])

    if not any("深圳金赋" in paragraph for paragraph in paragraphs):
        paragraphs.insert(
            -1,
            f"深圳金赋会围绕{short_topic}这类政策，先用补贴平台做企业画像和政策匹配，再提示材料缺口、项目优先级和后续培育方向。",
        )
    if not any("金赋补贴宝" in paragraph for paragraph in paragraphs):
        paragraphs.append(closing_options[(variant + 4) % len(closing_options)])
    article_chars = sum(len(paragraph) for paragraph in paragraphs)
    padding_round = 0
    while article_chars < 900 and padding_round < 2:
        padding = padding_options[(variant + padding_round) % len(padding_options)]
        if padding in paragraphs:
            padding = extra_options[(variant + padding_round + 1) % len(extra_options)]
        if padding in paragraphs:
            padding = f"再补一句：围绕{short_topic}，企业更需要先看自身项目和材料是否成熟，再决定要不要投入申报准备。"
        paragraphs.insert(-1, padding)
        article_chars = sum(len(paragraph) for paragraph in paragraphs)
        padding_round += 1
    if article_chars < 780:
        concise_fillers = [
            f"这类政策最适合提前规划。企业可以把研发、人才、设备、市场、合规等高频投入统一放进年度补贴清单，先看哪些已经具备条件，哪些还需要继续养资料。",
            f"从拿补贴的角度看，政策机会不是单独一份通知，而是企业经营能力的侧面证明。项目事实、费用路径、成果资料和合规记录越清楚，平台判断越准确。",
            f"如果企业正在做降本增效，这类政策就不该只在文件夹里停留。把真实投入和专项资金匹配起来，能帮助企业看到成本背后的补贴、奖励和配套机会。",
            f"对成长快的企业来说，项目推进、团队扩张和资金投入往往同步发生。现在把合同、票据、数据和成果核清楚，后面遇到申报窗口时就能少补很多解释材料。",
            f"企业也可以把这次评估当成一次内部协同：财务核票据，项目核过程，业务核成果，管理层确认申报优先级，补贴平台负责把条件和材料串起来。",
            f"如果企业暂时达不到申报条件，也不用气馁。补贴平台会记录当前差距，等资质提升、项目成熟或资料补齐后，再重新匹配同类专项资金机会。",
            f"很多企业真正损失的不是补贴金额，而是没有建立政策台账。高频投入项目更需要把合同、发票、付款、成果和归档说明持续更新，避免窗口来了却找不到依据。",
            f"这类政策还提醒企业：补贴申报不是临时动作，而是经营管理的一部分。平时把资料留好，年度做专项资金测算时，才更容易看见可争取的空间。",
            f"对负责人来说，这类政策的价值很直接：已经发生的经营投入，有机会通过政策匹配变成资金回流。先测一轮，不耽误经营，也能提前知道机会大小。",
            f"企业如果已经有相关项目，更应该把主体资质、费用凭证、项目成果和申报口径做一次完整核验。只要基础条件能对上，后续材料准备就有了明确方向。",
        ]
        filler = concise_fillers[variant % len(concise_fillers)]
        if filler not in paragraphs:
            paragraphs.insert(-1, filler)
            article_chars = sum(len(paragraph) for paragraph in paragraphs)
        if article_chars < 700:
            second_filler = concise_fillers[(variant + 3) % len(concise_fillers)]
            if second_filler not in paragraphs:
                paragraphs.insert(-1, second_filler)
                article_chars = sum(len(paragraph) for paragraph in paragraphs)
    return {
        "title": title,
        "source": source,
        "valid_period": "以政策原文及后续申报指南为准",
        "max_amount": "以政策原文及后续申报指南为准",
        "from_url": url,
        "article_title": article_title,
        "paragraphs": paragraphs,
    }

def format_period(start: object, end: object) -> str:
    start_text = str(start or "").strip()
    end_text = str(end or "").strip()
    if start_text and end_text:
        return f"{start_text}至{end_text}"
    return start_text or end_text or "以申报指南为准"


def format_amount(max_amount: object) -> str:
    amount = str(max_amount or "").strip()
    if not amount:
        return "以申报指南为准"
    if "万" in amount or "元" in amount:
        return amount
    return f"最高{amount}万元"


def choose_article_angle(title: str) -> tuple[str, str, str]:
    if "训力券" in title or "算力" in title:
        return (
            "AI企业如何把算力投入变成政策机会？",
            "这类政策通常适合大模型训练、算法研发、智能制造、自动驾驶、具身智能、AI医药、AI设计、AI质检等方向。企业判断申报价值时，不能只看是否采购了算力，还要看训练任务是否与研发项目直接相关，合同、发票、支付凭证、算力使用记录、项目技术说明和成果产出是否能够形成完整证据链。",
            "深圳金赋本身以人工智能和数据应用为技术核心，长期运营补贴平台，更理解AI企业在算力、模型、研发和应用示范之间的政策组合关系。平台可帮助企业把算力投入拆解成研发项目、费用台账、申报窗口、材料清单和风险提示，减少因材料口径不一致导致的补正成本。",
        )
    if "会展" in title or "展会" in title:
        return (
            "展会主办方如何提高申报准备效率？",
            "会展类政策的难点在于材料复合度高，既要证明展会真实举办，也要说明专业观众、参展企业、产业带动、宣传效果和费用支出的合理性。主办方需要提前整理合同、发票、付款凭证、现场照片、宣传报道、参展商清单、观众数据和项目总结，避免临近截止才发现证据不足。",
            "深圳金赋可将政策条款拆成可执行清单，帮助会展企业对照申报条件建立费用台账、参展商台账、宣传台账和成果转化台账。依托补贴平台，企业还可以继续跟踪商务、文旅、促消费、招商和产业集群类政策，把一次展会补贴申报延伸为长期品牌资产管理。",
        )
    if "专精特新" in title or "企业培育" in title or "单项冠军" in title:
        return (
            "专精特新和成长型企业如何提前布局？",
            "企业培育类政策往往与专精特新、小巨人、单项冠军、高新技术企业、研发投入、知识产权和主导产品市场表现紧密相关。即便部分项目采用免申即享，企业也不能等政策上门，而要提前把研发台账、财务数据、知识产权、质量管理、客户案例和荣誉资质做扎实。",
            "深圳金赋服务企业政策匹配时，会把当下可申报补贴和未来资质培育路径一起看。补贴平台可按区域、行业、营收、研发投入、知识产权、社保人数和资质进度进行标签匹配，并进一步帮助企业生成年度申报地图，识别先补哪些短板、先准备哪些材料、哪些时间节点必须跟进。",
        )
    return (
        "企业如何快速判断申报价值？",
        "企业面对一条新政策时，首先要判断政策对象、区域范围、申报时间、资助标准、费用范围、材料要求和不重复享受限制。只看最高金额容易误判，真正影响申报结果的是企业资质、项目周期、费用凭证、绩效目标和材料一致性。",
        "深圳金赋科技有限公司依托补贴平台沉淀1100万条全国四级公开政策数据，并通过补贴平台提供政策匹配、资质测评、申报清单和节点提醒，帮助企业把政策原文转化为可执行的申报计划。",
    )


def build_article_from_policy(row: dict[str, object]) -> dict[str, object]:
    title = str(row.get("title") or "未命名政策")
    source = str(row.get("from_bm") or row.get("department") or "政策发布部门")
    valid_period = format_period(row.get("declare_start_time") or row.get("start_time"), row.get("declare_end_time") or row.get("end_time"))
    max_amount = format_amount(row.get("max_amount"))
    policy_text = strip_html(str(row.get("content") or ""))
    article_suffix, target_guidance, jinfu_guidance = choose_article_angle(title)
    article_title = make_db_article_title(title, article_suffix)
    summary = policy_text[:220] if policy_text else f"{source}发布相关扶持政策，企业可结合自身资质和项目阶段关注申报机会。"
    paragraphs = [
        f"{title}已经发布，政策来源为{source}，申报或有效周期为{valid_period}，资助亮点为{max_amount}。从政策原文看，核心信息可以概括为：{summary}。对企业来说，这类政策不只是新闻信息，更应该转化为年度经营、研发、人才、市场或产业项目规划中的具体动作。",
        target_guidance,
        "很多企业错过补贴，不是因为完全不符合条件，而是没有在政策窗口期前完成资质判断和材料整理。建议企业先核验注册地、行业方向、项目实施地、营收规模、研发投入、知识产权、合同发票、付款凭证、项目成果、信用记录等关键要素，再决定是否投入申报。对于需要审计、专家评审、现场核查或纸质材料提交的项目，更要提前建立资料台账。",
        jinfu_guidance,
        f"如果你希望直接从企业自身情况出发，判断这条政策是否值得申报，并同步发现其他可叠加关注的区级、市级、省级和国家级补贴机会，{CTA}",
    ]
    return {
        "title": title,
        "source": source,
        "valid_period": valid_period,
        "max_amount": max_amount,
        "from_url": row.get("from_url") or "",
        "article_title": article_title,
        "paragraphs": paragraphs,
    }


def parse_ids(raw_ids: str) -> list[str]:
    return [item.strip() for item in re.split(r"[,，\s]+", raw_ids or "") if item.strip()]


def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def load_policies_from_mysql(policy_ids: list[str], limit: int) -> list[dict[str, object]]:
    if importlib.util.find_spec("pymysql") is None:
        raise RuntimeError("PyMySQL is required for --from-db. Install it with: python -m pip install PyMySQL")
    import pymysql

    connection = pymysql.connect(
        host=require_env("MYSQL_HOST"),
        user=require_env("MYSQL_USER"),
        password=require_env("MYSQL_PASSWORD"),
        database=require_env("MYSQL_DBNAME"),
        port=int(os.environ.get("MYSQL_PORT", "3306")),
        charset=os.environ.get("MYSQL_CHARSET", "utf8mb4"),
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with connection.cursor() as cursor:
            columns = "id, api_id, title, start_time, end_time, declare_start_time, declare_end_time, max_amount, content, from_bm, department, from_url, region"
            if policy_ids:
                placeholders = ", ".join(["%s"] * len(policy_ids))
                sql = f"SELECT {columns} FROM policy_info WHERE id IN ({placeholders}) OR api_id IN ({placeholders}) ORDER BY update_time DESC, create_time DESC"
                cursor.execute(sql, [*policy_ids, *policy_ids])
            else:
                sql = f"SELECT {columns} FROM policy_info ORDER BY update_time DESC, create_time DESC LIMIT %s"
                cursor.execute(sql, (limit,))
            return list(cursor.fetchall())
    finally:
        connection.close()


def ordered_unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    unique_items: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        unique_items.append(item)
    return unique_items


def resolve_articles(from_db: bool, ids: str, limit: int, urls: str, variants_per_url: int = 1) -> list[dict[str, object]]:
    if from_db:
        rows = load_policies_from_mysql(parse_ids(ids), limit)
        if not rows:
            raise RuntimeError("No policy rows found from MySQL with the provided filters.")
        return [build_article_from_policy(row) for row in rows]

    selected_urls = ordered_unique(parse_ids(urls) if urls else POLICY_URLS)
    variants_per_url = max(1, variants_per_url)
    articles: list[dict[str, object]] = []
    index = 1
    for url in selected_urls:
        for _ in range(variants_per_url):
            articles.append(build_article_from_url(url, index))
            index += 1
    return articles


def sanitize_windows_filename(name: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', name).strip().rstrip('.')
    return cleaned[:180] or "policy_article"

def unique_article_title(title: str, used_titles: dict[str, int]) -> str:
    normalized = normalize_article_title(title)
    count = used_titles.get(normalized, 0) + 1
    used_titles[normalized] = count
    if count == 1:
        return normalized
    suffix = f"-{count:02d}"
    return f"{normalized[: TITLE_MAX_CHARS - len(suffix)]}{suffix}"


def unique_docx_filename(title: str, used_filenames: set[str]) -> str:
    filename_base = sanitize_windows_filename(title)
    output_name = f"{filename_base}.docx"
    filename_count = 2
    while output_name in used_filenames:
        output_name = f"{filename_base}-{filename_count:02d}.docx"
        filename_count += 1
    used_filenames.add(output_name)
    return output_name


def paragraph_xml(text: str, style: str | None = None) -> str:
    style_xml = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
    return f'<w:p>{style_xml}<w:r><w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>'


def create_docx(path: Path, title: str, paragraphs: list[str]) -> None:
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>"""
    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>"""
    word_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>"""
    styles = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:rFonts w:ascii="SimSun" w:eastAsia="SimSun"/><w:sz w:val="22"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:rPr><w:b/><w:rFonts w:ascii="Microsoft YaHei" w:eastAsia="Microsoft YaHei"/><w:sz w:val="32"/></w:rPr></w:style></w:styles>"""
    body = paragraph_xml(title, "Title") + "".join(paragraph_xml(p) for p in paragraphs)
    document = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>{body}<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr></w:body></w:document>"""
    with ZipFile(path, "w", ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", content_types)
        docx.writestr("_rels/.rels", rels)
        docx.writestr("word/_rels/document.xml.rels", word_rels)
        docx.writestr("word/styles.xml", styles)
        docx.writestr("word/document.xml", document)


def article_markdown(article: dict[str, object]) -> str:
    paragraphs = article["paragraphs"]
    assert isinstance(paragraphs, list)
    return "\n\n".join([f"# {article['article_title']}", *paragraphs])


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate promotional policy articles as DOCX files and Markdown.")
    parser.add_argument("--from-db", action="store_true", help="Read policy rows from MySQL using MYSQL_* environment variables.")
    parser.add_argument("--ids", default="", help="Comma/space separated policy id or api_id values to fetch when --from-db is used.")
    parser.add_argument("--limit", type=int, default=10, help="Number of latest MySQL rows to fetch when --from-db is used without --ids.")
    parser.add_argument("--urls", default="", help="Comma/space separated policy URLs. Defaults to the current request's URL list.")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR), help="Directory for generated DOCX files.")
    parser.add_argument("--variants-per-url", type=int, default=DEFAULT_VARIANTS_PER_URL, help="Generate multiple article variants for each URL in URL mode.")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    articles = resolve_articles(args.from_db, args.ids, args.limit, args.urls, args.variants_per_url)

    generated_docs = []
    used_titles: dict[str, int] = {}
    used_filenames: set[str] = set()
    for article in articles:
        article = dict(article)
        article["article_title"] = unique_article_title(str(article["article_title"]), used_titles)
        output_name = unique_docx_filename(str(article["article_title"]), used_filenames)

        output_path = output_dir / output_name
        create_docx(output_path, str(article["article_title"]), article["paragraphs"])
        generated_docs.append((output_name, article))

    doc_list = "\n".join(f"- `{output_name}`" for output_name, _ in generated_docs)
    article_sections = []
    for index, (output_name, article) in enumerate(generated_docs, start=1):
        article_sections.append(
            f"## 政策{index}：{article['title']}\n\n"
            f"- Word文件：`{output_name}`\n"
            f"- 政策来源：{article['source']}\n"
            f"- 有效期：{article['valid_period']}\n"
            f"- 资助亮点：{article['max_amount']}\n"
            f"- 文章标题：{article['article_title']}\n\n"
            f"{article_markdown(article)}"
        )

    joined_article_sections = "\n\n".join(article_sections)
    (output_dir / "generated_documents.md").write_text(
        "# 生成的Word文档列表\n\n"
        f"{doc_list}\n\n"
        "# 文章内容\n\n"
        f"{joined_article_sections}\n",
        encoding="utf-8",
    )
    for output_name, _ in generated_docs:
        print(output_dir / output_name)


if __name__ == "__main__":
    main()
