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
CTA = "可关注公众号「金赋补贴宝」，通过公众号访问补贴平台，进行企业资质评估和政策匹配，获取更适合自身情况的补贴推荐清单。"

# 默认只输出当前用户本轮提供的政策链接。
POLICY_URLS = ['http://www.sz.gov.cn/zfgb/2023/gb1298/content/post_10775907.html',
 'http://gxj.sz.gov.cn/gkmlpt/content/10/10666/post_10666715.html#25192',
 'http://www.szft.gov.cn/bmxx/qgxj/tzgg/content/post_10643552.html',
 'http://www.szlhq.gov.cn/bmxxgk/jjcjj/dtxx_124217/tzgg_124219/content/post_10642759.html',
 'http://gxj.sz.gov.cn/xxgk/xxgkml/qt/tzgg/content/post_10630981.html',
 'http://www.szlhq.gov.cn/xxgk/xwzx/tzgg/content/post_10353433.html',
 'http://pnr.sz.gov.cn/gkmlpt/content/10/10582/post_10582810.html',
 'http://jr.sz.gov.cn/sjrb/xxgk/zcfg/gfxwjcx/content/post_10401580.html',
 'http://commerce.sz.gov.cn/gkmlpt/content/10/10005/post_10005643.html',
 'http://www.szlhq.gov.cn/lhrlzyj/gkmlpt/content/9/9310/post_9310043.html',
 'http://www.szlh.gov.cn/lhmzj/gkmlpt/content/10/10123/post_10123830.html',
 'http://sf.sz.gov.cn/gfxwjcx/content/post_3003213.html',
 'http://sf.sz.gov.cn/gfxwjcx/content/post_3011829.html',
 'https://shenzhen.chinatax.gov.cn/sztax/zdgkml/gkmlzcfg/gkmlzcwj/202104/ea98a93b4e2746bcae825cd3e6cd009c.shtml',
 'http://www.szns.gov.cn/nsqqyfzfwzx/gkmlpt/content/10/10137/post_10137482.html#15685',
 'http://www.szns.gov.cn/nswhgdlyty/gkmlpt/content/10/10027/post_10027443.html#15246',
 'http://www.szns.gov.cn/nsqrzj/gkmlpt/content/9/9979/post_9979770.html#15130',
 'http://www.szns.gov.cn/nsqzfb/gkmlpt/content/10/10269/post_10269722.html#19454',
 'https://shenzhen.chinatax.gov.cn/sztax/zdgkml/gkmlzcfg/gkmlzcwj/202104/edf3abad26dc44498154d89b36abfddb.shtml',
 'http://www.szft.gov.cn/xxgk/zwgk/zcfg/bmgfx/content/post_9936698.html',
 'http://www.szlhq.gov.cn/gkmlpt/content/9/9606/post_9606416.html',
 'https://shenzhen.chinatax.gov.cn/sztax/zcwj/zcjd/202107/fc4e823da7ce415bbc66910ec4f50f11.shtml',
 'http://sf.sz.gov.cn/gfxwjcx/content/post_3012308.html',
 'http://szfb.sz.gov.cn/gkmlpt/content/5/5534/post_5534372.html',
 'http://zjj.sz.gov.cn/csml/zcfg/xxgk/zcfg_1/zcfg/gjj/content/post_9499279.html',
 'http://www.sz.gov.cn/zfgb/2021/gb1221/content/post_9439319.html',
 'http://zjj.sz.gov.cn/csml/zcfg/xxgk/zcfg_1/zcfg/content/post_9870992.html',
 'http://commerce.sz.gov.cn/xxgk/zcfgjzcjd/zcfg/content/post_9868030.html',
 'http://www.szft.gov.cn/xxgk/zwgk/zcfg/qzfwj/bgsgfxwj/content/post_9932533.html',
 'http://www.szft.gov.cn/xxgk/zwgk/zcfg/qzfwj/bgsgfxwj/content/post_9932532.html',
 'http://www.sz.gov.cn/zfgb/2022/gb1248/content/post_9919053.html',
 'http://sf.sz.gov.cn/gfxwjcx/content/post_9134033.html',
 'http://www.sz.gov.cn/zfgb/2022/gb1243/content/post_9840800.html',
 'http://sf.sz.gov.cn/gfxwjcx/content/post_9774760.html',
 'http://commerce.sz.gov.cn/xxgk/zcfgjzcjd/zcfg/content/post_9750939.html',
 'http://www.dpxq.gov.cn/xxgk/xxgk/zcfg/wj/xqgfxwj/content/post_9778707.html',
 'http://sf.sz.gov.cn/gfxwjcx/content/post_9779154.html',
 'http://commerce.sz.gov.cn/xxgk/zcfgjzcjd/zcfg/content/post_9734854.html',
 'http://sf.sz.gov.cn/gfxwjcx/content/post_9733690.html',
 'http://sf.sz.gov.cn/gfxwjcx/content/post_9731259.html',
 'http://sf.sz.gov.cn/gfxwjcx/content/post_9704623.html',
 'http://www.sz.gov.cn/zfgb/2022/gb1238/content/post_9714686.html',
 'http://jr.sz.gov.cn/sjrb/xxgk/zcfg/gfxwjcx/content/post_9683625.html',
 'http://jr.sz.gov.cn/gkmlpt/content/9/9683/post_9683389.html',
 'http://www.sz.gov.cn/zfgb/2022/gb1236/content/post_9684588.html',
 'http://jr.sz.gov.cn/gkmlpt/content/9/9683/post_9683115.html',
 'http://gxj.sz.gov.cn/gkmlpt/content/9/9626/post_9626193.html',
 'http://www.szft.gov.cn/ftqwtzx/gkmlpt/content/9/9544/post_9544699.html',
 'http://www.yantian.gov.cn/gkmlpt/content/9/9590/post_9590380.html']

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
}


PROMOTION_PLANS = [('市政府公报里的扶持信号，企业别只当资料存档', '深圳科技、制造、服务业、商贸和成长型企业', '市级规范文件、产业方向、资金管理、申报条件、企业责任和监督要求', '政策台账、项目资料、财务报表、合同票据、信用记录、成果说明和内部分工'),
 ('工信项目窗口来了，企业先把项目和费用对上号',
  '深圳制造业、软件信息、智能终端、工业互联网和产业链配套企业',
  '市级工信项目、产业专项、项目建设期、投入费用、技术成果、市场应用和材料完整性',
  '营业执照、财务报表、项目合同、发票付款、设备软件清单、知识产权、客户案例和验收资料'),
 ('福田工信通知别只转发，项目成熟度才是关键', '福田区制造业、软件信息、专精特新、数字化转型和工业服务企业', '区级工信扶持、项目投入、企业资质、技术成果、经营贡献和申报窗口', '企业资质、财务报表、项目合同、费用票据、技术资料、荣誉证书和成果说明'),
 ('龙华产业企业看通知，要把投入变成可申报项目', '龙华区制造业、商贸服务、数字经济、智能制造和成长型企业', '产业扶持、项目建设、经营贡献、技术改造、空间载体和企业培育', '营业执照、纳税数据、项目清单、合同发票、付款凭证、人员社保和发展计划'),
 ('工信政策更新后，企业要先做一轮补贴体检', '深圳工业、软件、信息服务、智能终端和产业链企业', '资助类别、项目费用、技术成果、行业应用、市场推广和企业资质', '营业执照、财务报表、合同发票、付款凭证、知识产权、客户案例和项目总结'),
 ('龙华企业遇到新通知，别等截止前才整理材料', '龙华区科技、制造、商贸、数字经济和专业服务企业', '区域扶持、经营贡献、项目投入、资质培育、空间载体和人才服务', '企业画像、项目台账、财务数据、合同票据、人员社保、资质证书和成果资料'),
 ('空间规划也会影响补贴，企业选址和项目要一起看', '园区运营、产业空间、制造业、物流仓储和城市更新相关企业', '用地空间、项目合规、产业布局、建设条件、运营场景和政策衔接', '租赁合同、用地资料、项目备案、建设方案、费用凭证、运营数据和合规证明'),
 ('金融政策不是银行才看，融资企业也要提前留痕', '科技企业、专精特新企业、拟上市企业和需要融资支持的成长型企业', '贷款贴息、融资担保、上市培育、风险补偿、绿色金融和产业基金', '授信合同、借款合同、利息凭证、担保资料、财务报表、资金用途和项目进展'),
 ('商务类政策看似宽，企业要找到自己的经营场景', '商贸流通、跨境电商、会展服务、消费品牌和外贸服务企业', '商贸消费、外贸发展、会展活动、品牌建设、市场拓展和经营贡献', '销售数据、活动方案、服务合同、发票付款、宣传资料、客户订单和效果报告'),
 ('龙华人才政策也能助力企业留人，别只让HR单独看', '龙华区科技企业、制造业企业、成长型企业和人力资源负责人', '人才引进、技能提升、就业服务、用工保障、员工稳定和企业发展', '员工名册、社保记录、劳动合同、培训资料、人才认定、岗位说明和企业福利台账'),
 ('罗湖民生服务项目，企业也能从服务台账里找机会', '罗湖区社会组织、民生服务、养老托育、社区运营和专业服务机构', '社会服务、机构规范、项目投入、服务人数、场地条件和社会效益', '机构资质、服务记录、场地合同、人员证书、费用票据、满意度反馈和项目总结'),
 ('法规文件别只存档，合规经营也关系到补贴申报', '各类需要规范经营、合同管理、信用管理和风险控制的企业', '依法经营、合同合规、信用记录、知识产权、争议处理和申报风险防控', '合同台账、制度文件、信用记录、知识产权资料、整改说明、审批记录和内部流程'),
 ('政策规则变化时，企业材料口径也要跟着更新', '深圳制造业、科技服务、商贸文旅、金融服务和创新型企业', '政策调整、申报条件、材料口径、审核规则、信用管理和不重复享受要求', '政策台账、项目清单、财务数据、合同票据、人员资料、资质证书和申报记录'),
 ('税务资料别只报税用，也能成为补贴申报底层证据', '科技、制造、商贸服务、跨境业务和成长型企业财务团队', '税收政策、纳税信用、发票合规、费用归集、研发投入和经营数据', '纳税申报表、发票台账、财务报表、研发费用、合同资料、付款凭证和税务信用记录'),
 ('南山企业服务政策，适合先做一次资质扫描', '南山区科技、软件信息、智能制造、文化创意和现代服务企业', '区级产业政策、创新项目、企业培育、空间支持、研发投入和经营贡献', '研发资料、项目合同、财务报表、知识产权、人员社保、场地材料和成果证明'),
 ('南山文旅体育项目，内容热度要沉淀成可申报证据', '南山区文旅活动、体育赛事、文化空间、数字文创和消费运营企业', '活动性质、举办周期、投入费用、参与人数、宣传传播、安全保障和社会效益', '活动方案、合同发票、付款凭证、现场照片、媒体报道、客流数据和复盘报告'),
 ('南山人力资源政策，招聘和培训也要有项目意识', '南山区科技企业、服务业企业、人力资源机构和成长型企业', '人才招聘、技能培训、就业服务、用工稳定、人才认定和企业培育', '招聘记录、劳动合同、社保缴纳、培训资料、人员证书、岗位说明和企业发展材料'),
 ('南山区级资金机会多，企业要先按项目分层', '南山区科技创新、软件信息、智能制造、现代服务和总部经济企业', '产业扶持、研发投入、经营贡献、空间载体、项目建设和企业梯度培育', '企业画像、项目台账、财务报表、合同票据、知识产权、人员资料和成果证明'),
 ('税务合规做得好，补贴申报材料也会更稳', '各类有研发投入、项目费用、销售收入和政策申报需求的企业', '税收优惠、费用归集、发票管理、纳税信用、研发加计和经营数据', '发票台账、纳税申报、财务报表、研发明细、合同付款、项目凭证和信用记录'),
 ('福田部门政策要落到项目，别只看文件名称', '福田区科技、商贸、金融、专业服务和文化消费企业', '区级资金事项、项目条件、经营贡献、申报窗口、材料成熟度和绩效要求', '申请资料、经营数据、合同发票、付款凭证、租赁材料、人员社保和成果报告'),
 ('龙华企业看区级政策，先把年度项目排个队', '龙华区制造业、数字经济、商贸服务、科技创新和成长型企业', '企业培育、项目投入、产业空间、科技创新、经营贡献和人才服务', '企业画像、项目台账、财务报表、合同票据、人员社保、资质证书和发展计划'),
 ('税收政策读懂后，企业可以顺手更新补贴地图', '科技型企业、制造业企业、跨境服务、商贸企业和财务负责人', '税务政策、纳税信用、费用归集、研发投入、收入确认和合规经营', '纳税资料、财务报表、发票台账、研发费用、合同付款、税务信用和项目说明'),
 ('法律规则不是离补贴很远，合规底子会影响申报质量', '各类拟申报专项资金、资质认定和产业扶持的企业', '依法经营、信用管理、合同规范、项目真实性、材料一致性和监督要求', '制度文件、合同台账、信用记录、审批资料、整改说明、项目凭证和内部分工'),
 ('地方金融政策窗口，成长型企业要算融资成本账', '科技企业、专精特新企业、拟上市企业、金融服务机构和融资平台', '贷款贴息、担保支持、上市培育、风险补偿、金融创新和产业资金', '授信合同、融资协议、利息凭证、担保资料、财务报表、资金用途和项目进展'),
 ('公积金和住房类政策，也可能影响企业用人成本', '用工规模较大的科技企业、制造业企业、园区企业和人力资源团队', '住房公积金、员工福利、用工成本、人才稳定、企业合规和职工权益', '员工名册、公积金记录、劳动合同、社保资料、薪酬制度、福利政策和人员台账'),
 ('市政府公报里的产业方向，企业要转成年度行动表', '深圳科技、制造、现代服务、金融商贸和成长型企业', '市级政策导向、产业重点、资金管理、项目条件、企业责任和监督要求', '政策台账、年度项目表、财务资料、合同票据、资质证书、成果案例和责任分工'),
 ('住建类政策看细节，项目资料越早整理越主动', '建筑施工、工程咨询、物业服务、园区运营和住房相关企业', '工程质量、安全管理、项目备案、住房服务、绿色建筑和信用评价', '工程合同、验收文件、人员证书、费用凭证、项目照片、信用记录和总结报告'),
 ('商务扶持政策适合做组合，别只盯单个项目', '外贸企业、跨境电商、会展服务、商贸流通和消费品牌企业', '外贸发展、市场开拓、商贸消费、品牌推广、会展活动和经营贡献', '销售数据、服务合同、活动方案、发票付款、宣传资料、订单记录和效果报告'),
 ('福田资金管理规则，企业要把申报材料做成闭环', '福田区科技、金融、商贸、专业服务和文化消费企业', '资金管理、项目条件、绩效目标、材料审核、信用记录和资金监管', '项目申请资料、财务报表、合同票据、付款凭证、信用记录、绩效说明和复盘材料'),
 ('福田政务规则变化，企业办补贴也要看口径变化', '福田区拟申报产业资金、人才政策和项目扶持的企业', '办事规则、材料口径、审核流程、信用要求、部门协同和政策更新', '企业资料、项目清单、合同票据、人员社保、信用记录、申报记录和责任分工'),
 ('市级产业政策发布后，企业要先找自己能做的项目', '深圳制造业、科技服务、现代服务、商贸消费和创新型企业', '市级资金支持、项目投入、创新成果、产业贡献、审核要求和绩效评价', '项目清单、财务报表、合同票据、付款凭证、知识产权、客户案例和成果证明'),
 ('法规检索里的政策，也可能影响企业补贴判断', '深圳科技、制造、服务业、商贸和成长型企业', '规范文件、政策口径、申报条件、资金管理、信用要求和监督责任', '政策台账、企业画像、项目清单、财务资料、合同票据、资质证明和内控制度'),
 ('政府公报里的条款，要变成企业自己的补贴提醒', '深圳各类产业企业、科技企业、商贸服务和专业服务机构', '公报文件、产业方向、项目条件、资金安排、绩效目标和材料要求', '政策记录、项目储备、财务数据、合同凭证、资质证书、成果材料和责任人清单'),
 ('规范文件一调整，企业申报策略也要跟着调整', '拟申报市区专项资金、资质认定和产业扶持的企业', '政策有效期、申报口径、支持对象、材料要求、不重复享受和信用管理', '政策台账、项目清单、申报记录、合同票据、财务资料、信用证明和复盘报告'),
 ('商务政策看市场成效，企业要会讲增长故事', '商贸流通、外贸服务、跨境电商、会展活动和消费品牌企业', '市场拓展、消费促进、品牌建设、外贸服务、活动成效和经营贡献', '销售数据、客户订单、活动照片、宣传材料、合同发票、付款凭证和复盘报告'),
 ('大鹏企业做项目，特色定位和落地证据都要有', '大鹏新区文旅、海洋、生态农业、民宿、体育和科技服务企业', '片区定位、特色产业、生态保护、项目投入、市场推广和安全管理', '项目方案、经营台账、合同票据、宣传资料、审批材料、安全记录和成效说明'),
 ('政策法规看起来远，企业资金申报其实离不开它', '深圳各类需要申报补贴、资质认定和政府项目的企业', '法规依据、企业责任、信用记录、材料真实性、项目监督和资金合规', '合同台账、制度文件、项目资料、信用记录、审批凭证、财务资料和整改说明'),
 ('商务项目办完以后，成交和传播数据别丢了', '商贸活动、会展服务、外贸企业、跨境电商和品牌运营企业', '展会活动、市场开拓、消费促进、品牌推广、交易数据和服务成效', '活动方案、参展资料、销售数据、客户订单、合同发票、宣传素材和复盘报告'),
 ('政策条文更新后，企业要检查材料有没有过期', '深圳科技、制造、商贸、文旅、金融和专业服务企业', '政策有效期、支持对象、材料口径、审核规则、信用管理和资金监管', '企业资料、项目清单、合同票据、财务报表、资质证书、信用记录和政策日历'),
 ('依法申报补贴，企业内部流程要先跑顺', '拟申报专项资金、项目扶持、资质认定和荣誉称号的企业', '依法申报、材料真实性、合同合规、费用归集、信用记录和内部审批', '内控制度、合同台账、财务凭证、项目资料、信用证明、审批记录和责任分工'),
 ('政策库不是资料堆，企业要把它变成机会池', '深圳制造业、科技服务、商贸文旅、金融服务和成长型企业', '政策趋势、产业重点、资金方向、企业培育、项目储备和材料规范', '企业画像、项目储备、费用台账、资质证书、合同票据、成果案例和政策日历'),
 ('政府公报中的资金规则，企业财务和项目要一起看', '深圳各类拟申报专项资金的科技、制造、服务和商贸企业', '资金管理、预算绩效、申报审核、重复申报限制、信用管理和项目监督', '项目台账、财务报表、合同票据、付款凭证、信用记录、绩效说明和内部制度'),
 ('金融支持政策密集，企业要把融资动作纳入补贴规划', '科技企业、专精特新企业、拟上市企业、金融机构和融资服务平台', '融资服务、贷款贴息、担保补助、上市培育、风险补偿和金融创新', '授信合同、借款合同、利息凭证、担保材料、财务报表、资金用途和经营数据'),
 ('金融机构服务企业，也要把服务成效留成证据', '金融服务机构、融资平台、担保机构、小贷机构和服务实体经济的机构', '金融服务、风险防控、实体经济支持、信息报送、合规经营和服务成效', '经营资质、内控制度、客户台账、服务合同、财务报表、风险说明和数据报送记录'),
 ('市级公报里的产业信号，适合做年度补贴复盘', '深圳科技、制造、金融、商贸、文旅和专业服务企业', '市级政策导向、产业资金、企业培育、项目条件、绩效管理和监督要求', '政策记录、项目清单、财务数据、合同票据、人员资料、资质荣誉和成果案例'),
 ('地方金融新口径下，企业融资凭证要留得更细', '科技成长型企业、专精特新企业、拟上市企业和金融服务机构', '金融监管、融资支持、贷款贴息、风险补偿、上市培育和信用管理', '融资合同、授信文件、利息凭证、担保资料、资金用途、财务报表和信用记录'),
 ('工信政策别只看名称，项目建设期和费用边界更重要', '深圳制造业、软件信息、智能制造、工业互联网和产业链企业', '技术改造、数字化转型、软件信息、设备投入、项目周期和费用边界', '项目立项、设备合同、软件清单、发票付款、研发资料、知识产权和应用成效'),
 ('福田文体活动想拿补贴，热度要转成可证明成效', '福田区文化体育、文旅活动、赛事运营、场馆服务和消费品牌企业', '活动运营、赛事组织、文化消费、宣传传播、客流数据和社会效益', '活动方案、合同发票、付款凭证、现场照片、媒体报道、客流数据和复盘报告'),
 ('盐田企业看区级政策，区域特色和经营贡献都要准备', '盐田区港口物流、文旅消费、现代服务、科技和绿色发展企业', '区域产业、经营贡献、项目投入、空间载体、绿色发展和绩效目标', '财务报表、纳税证明、项目合同、费用票据、绩效数据、信用记录和申报说明')]

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
    excerpt = "".join(selected)[:limit]
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

def make_article_title(plan_title: str, policy_title: str, index: int) -> str:
    subject = short_policy_subject(policy_title)
    if not subject or len(subject) < 4:
        return plan_title
    templates = [
        f"{subject}背后，企业要看到补贴线索",
        f"{subject}来了，别只收藏文件",
        f"读懂{subject}，先看企业能不能匹配",
        f"{subject}不只是通知，也是项目提醒",
        f"围绕{subject}，企业要提前整理证据",
    ]
    title = templates[(index - 1) % len(templates)]
    return title if len(title) <= 34 else plan_title

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
    plan = PROMOTION_PLANS[index - 1] if index - 1 < len(PROMOTION_PLANS) else PROMOTION_PLANS[-1]
    planned_title, audience, policy_focus, proof_materials = plan
    fetched_title = ""
    fetched_text = ""
    try:
        fetched_title, fetched_text = fetch_url_text(url)
    except (HTTPError, URLError, TimeoutError, OSError):
        fetched_title, fetched_text = "", ""
    policy_title = clean_policy_title(fetched_title)
    policy_signal = policy_excerpt(fetched_text)
    money_signal = subsidy_highlight(fetched_text)
    article_title = make_article_title(planned_title, policy_title, index)
    title = policy_title or planned_title
    policy_subject = short_policy_subject(policy_title) or planned_title
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
        f"从客户服务角度看，{short_topic}也是一次重新整理企业资产的机会：哪些投入能证明，哪些资质能加分，哪些项目还能延伸申报。补贴平台能帮助企业把这些信息沉淀下来，后续遇到新政策时快速复用。",
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
        f"如果企业想判断这类政策是否值得申报，并生成更贴合自身情况的补贴推荐清单，可关注公众号「金赋补贴宝」，通过公众号访问补贴平台，进行企业资质评估和政策匹配。",
        f"想知道{audience}现有项目能不能匹配这类机会，或者还缺哪些申报材料，可关注公众号「金赋补贴宝」，通过公众号访问补贴平台，先做一次企业资质评估。",
        f"近期有补贴申报、资质培育或项目资金规划需求的企业，可关注公众号「金赋补贴宝」，通过公众号访问补贴平台，查看适合自身情况的政策推荐。",
        f"如果{audience}不确定这类政策是否适合自己，建议先做一次资质评估和政策匹配。可关注公众号「金赋补贴宝」，通过公众号访问补贴平台，把企业资料转化为可执行的补贴清单。",
        f"企业也可以把这类机会作为年度补贴规划的起点。关注公众号「金赋补贴宝」，通过公众号访问补贴平台，先确认自身条件、材料缺口和可优先推进的政策方向。",
        f"不确定项目是否能申报，不建议只凭经验判断。关注公众号「金赋补贴宝」，通过公众号访问补贴平台，让系统先根据企业信息做匹配，再决定是否进入材料准备。",
        f"如果企业已经有项目投入，但不知道能否形成补贴申请，可关注公众号「金赋补贴宝」，通过公众号访问补贴平台，先完成资质评估，再对照推荐清单安排申报节奏。",
        f"政策机会不会一直停留在通知里，关键是企业能不能及时行动。关注公众号「金赋补贴宝」，通过公众号访问补贴平台，把相关信息转化为自己的补贴评估结果。",
    ]
    variant = (index - 1)
    style = variant % 8
    if style == 0:
        paragraphs = [
            f"深圳金赋成立于2017年，长期围绕企业补贴申报做政策匹配和材料管理，补贴平台沉淀了1100万条全国四级公开政策数据。说白了，{short_topic}不是让企业多看一条通知，而是提醒企业看看手上的项目能不能变成补贴机会。{opening_options[variant % len(opening_options)]}",
            f"对{audience}来说，重点不是把政策读得多细，而是把{policy_focus}和真实业务对上号。能对上的地方，就是值得优先评估的机会；对不上的地方，也能反过来提醒企业补短板。",
            f"材料也不用一开始就想得很复杂，可以先把{proof_materials}集中到一个项目资料夹里。合同、票据、照片、数据、成果说明放在一起，后面不管是评估还是申报，都会轻松很多。",
            company_options[(variant + 3) % len(company_options)],
            f"这类政策真正的价值，不只是当下有没有补贴，而是帮企业养成项目留痕的习惯。{value_options[(variant + 4) % len(value_options)]}",
            service_options[(variant + 7) % len(service_options)],
            closing_options[(variant + 8) % len(closing_options)],
        ]
    elif style == 1:
        paragraphs = [
            f"深圳金赋服务企业时，常见的第一类问题就是：政策很多，但不知道哪条真正适合自己。这篇更适合给{audience}做一次轻量提醒：先看{short_topic}能不能落到现有项目。{opening_options[(variant + 1) % len(opening_options)]}",
            f"先别急着问“能补多少”，更应该先问“我有没有类似项目”。如果企业正在做{policy_focus}相关工作，那就值得把项目投入、成果和证明材料先盘一遍。",
            f"再看材料是不是拿得出来。{proof_materials}这些内容，平时看起来只是日常资料，放到政策场景里就可能变成判断企业能不能拿补贴的关键证据。",
            f"深圳金赋想帮企业解决的，正是“政策很多但不知道哪条适合我”的问题。{company_options[(variant + 5) % len(company_options)]}",
            f"所以，这类政策可以当成一次经营提醒：项目要留痕，费用要规范，成果要能讲清楚。{review_options[(variant + 6) % len(review_options)]}",
            closing_options[(variant + 7) % len(closing_options)],
        ]
    elif style == 2:
        paragraphs = [
            f"深圳金赋做补贴平台时，经常会把政策机会先翻译成老板能看懂的投入产出账。从老板视角看，{short_topic}其实不是一条孤立通知，而是一道经营管理题。{opening_options[(variant + 2) % len(opening_options)]}",
            f"老板关心的是：企业已经花出去的钱、已经做完的项目、已经沉淀的资质，有没有可能换回政策资金。围绕{policy_focus}，只要能找到业务事实和证明材料，就有进一步评估的价值。",
            f"财务这边也很关键。围绕{short_topic}，合同、发票、付款、费用归集和项目名称如果前后不一致，再好的项目也容易卡住。{material_options[(variant + 4) % len(material_options)]}",
            f"项目负责人则要把过程讲清楚：为什么做、怎么做、做出什么效果。说到底，补贴不是“写出来”的，而是靠真实投入和可验证成果支撑出来的。",
            f"补贴平台适合先做一轮筛查，看看哪些项目值得申，哪些项目还需要养一养。{service_options[(variant + 6) % len(service_options)]}",
            next_step_options[(variant + 7) % len(next_step_options)],
            closing_options[(variant + 8) % len(closing_options)],
        ]
    elif style == 3:
        paragraphs = [
            f"可以把{short_topic}想成一张项目便签：适合谁、看什么项目、需要什么证据、现在要不要行动。{opening_options[variant % len(opening_options)]}",
            f"适合谁？主要看{audience}能不能和政策方向对上。尤其是{policy_focus}这些点，越贴近企业真实业务，后续越值得跟进。",
            f"看什么项目？看已经发生的投入，也看接下来准备推进的计划。项目目标、投入内容、执行周期、成果数据越清楚，补贴评估越有底。{match_options[(variant + 4) % len(match_options)]}",
            f"需要什么证据？先把{proof_materials}放进同一个资料夹，别让项目资料散落在不同同事手里。{material_options[(variant + 5) % len(material_options)]}",
            f"现在要不要行动？如果材料已经七八成齐，就可以进入评估；如果还差不少，也可以先放进培育清单。补贴平台能把这些状态动态记录下来，避免企业错过窗口。",
            company_options[(variant + 7) % len(company_options)],
            closing_options[(variant + 8) % len(closing_options)],
        ]
    elif style == 4:
        paragraphs = [
            f"这类政策最怕的不是看不懂，而是觉得“好像和我有关”，结果真准备时发现证据不够。{opening_options[(variant + 1) % len(opening_options)]}",
            f"别只看名称相关。{audience}要先确认业务方向、项目周期和投入内容是否能对应{policy_focus}，否则很容易花了时间却发现匹配度不高。",
            f"也别只堆材料。{proof_materials}要能串成一个完整故事：企业为什么做这个项目，钱花在哪里，最后形成了什么效果。{material_options[(variant + 6) % len(material_options)]}",
            f"还有一个常见情况：多个政策看起来都能申，但同一笔费用不能反复用。企业最好提前把费用边界标清楚，后面沟通会省很多事。{next_step_options[(variant + 7) % len(next_step_options)]}",
            f"深圳金赋补贴平台的作用，就是把这些问题提前暴露出来。{company_options[(variant + 1) % len(company_options)]}",
            service_options[(variant + 2) % len(service_options)],
            closing_options[(variant + 3) % len(closing_options)],
        ]
    elif style == 5:
        paragraphs = [
            f"假设你们刚做完一个项目，现在看到{short_topic}相关政策，可以先别急着写申报材料，先把项目复盘一遍。{opening_options[(variant + 2) % len(opening_options)]}",
            f"复盘时可以聊得很直白：这个项目为什么做？花了多少钱？谁参与？有没有数据？有没有客户、用户或现场成果？这些问题如果答得清楚，补贴评估就有基础。",
            f"再把资料找出来。{proof_materials}不只是普通资料，更像是项目的证据包。证据包越完整，后面政策匹配和申报判断就越快。",
            f"如果发现资料缺口，也没关系，早点发现反而是好事。能补说明的补说明，能补数据的补数据，能补成果的补成果，别等到窗口快关了才着急。",
            f"深圳金赋会把复盘结果放进补贴平台，形成企业自己的政策资产库。{company_options[(variant + 2) % len(company_options)]}",
            f"以后同类政策再出现时，企业就不用从零开始翻资料。{value_options[(variant + 3) % len(value_options)]}",
            closing_options[(variant + 4) % len(closing_options)],
        ]
    elif style == 6:
        paragraphs = [
            f"很多企业会问：这类政策到底和我有什么关系？围绕{short_topic}，可以用几个很接地气的问题来判断。{opening_options[variant % len(opening_options)]}",
            f"我的企业类型对吗？答案要回到{audience}以及政策面向的业务方向。{match_options[(variant + 7) % len(match_options)]}",
            f"我的项目能证明吗？答案要看{proof_materials}是否能支撑费用、过程和成果。如果只能口头说明，没有证据，那就还需要再补一补。",
            f"现在值得推进吗？如果材料成熟、金额清晰、成果可量化，就值得让补贴平台先做评估；如果短板明显，可以先进入政策培育。{service_options[(variant + 1) % len(service_options)]}",
            f"还有没有别的政策能一起看？{value_options[(variant + 2) % len(value_options)]}",
            f"补贴平台可以把这些问题变成线上评估，让企业先看到匹配结果和材料建议，再决定要不要继续投入精力。{company_options[(variant + 3) % len(company_options)]}",
            closing_options[(variant + 5) % len(closing_options)],
        ]
    else:
        paragraphs = [
            f"把{short_topic}放进年度补贴规划里看，企业会更容易找到节奏。{opening_options[(variant + 1) % len(opening_options)]}",
            f"先筛一遍：围绕{policy_focus}判断企业有没有机会、项目有没有基础、材料有没有雏形。{match_options[variant % len(match_options)]}",
            f"再补一补：围绕{short_topic}，把{proof_materials}按项目归档，统一命名、统一口径、统一负责人。{material_options[(variant + 1) % len(material_options)]}",
            f"然后定优先级：不是所有政策都要追，企业要先看匹配度、材料成熟度和资金价值。{value_options[(variant + 2) % len(value_options)]}",
            f"最后持续跟进：{next_step_options[(variant + 3) % len(next_step_options)]}",
            f"深圳金赋补贴平台可以把筛选、材料、优先级和提醒串起来，让{audience}从被动找政策变成主动管政策。{service_options[(variant + 4) % len(service_options)]}",
            closing_options[(variant + 6) % len(closing_options)],
        ]
    article_chars = sum(len(paragraph) for paragraph in paragraphs)
    if article_chars < 900:
        paragraphs.insert(
            -1,
            f"再说得实际一点，{audience}平时不一定有专人盯政策，但项目投入、客户案例、合同票据和经营成果每天都在发生。企业可以先把已有项目放进补贴平台做一次匹配，把能冲刺的机会、需要培育的条件和暂时不适合的项目分开看。这样不会把政策当成临时任务，而是变成一套能持续复用的补贴管理方法。",
        )
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
    article_title = f"{title[:24]}：{article_suffix}"
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


def resolve_articles(from_db: bool, ids: str, limit: int, urls: str) -> list[dict[str, object]]:
    if from_db:
        rows = load_policies_from_mysql(parse_ids(ids), limit)
        if not rows:
            raise RuntimeError("No policy rows found from MySQL with the provided filters.")
        return [build_article_from_policy(row) for row in rows]

    selected_urls = parse_ids(urls) if urls else POLICY_URLS
    return [build_article_from_url(url, index) for index, url in enumerate(selected_urls, start=1)]


def sanitize_windows_filename(name: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', name).strip().rstrip('.')
    return cleaned[:180] or "policy_article"


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
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    articles = resolve_articles(args.from_db, args.ids, args.limit, args.urls)

    generated_docs = []
    for article in articles:
        output_name = sanitize_windows_filename(str(article["article_title"])) + ".docx"
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
            f"- 推广文章：{article['article_title']}\n\n"
            f"{article_markdown(article)}"
        )

    joined_article_sections = "\n\n".join(article_sections)
    (output_dir / "generated_documents.md").write_text(
        "# 生成的Word文档列表\n\n"
        f"{doc_list}\n\n"
        "# 推广文章内容\n\n"
        f"{joined_article_sections}\n",
        encoding="utf-8",
    )
    for output_name, _ in generated_docs:
        print(output_dir / output_name)


if __name__ == "__main__":
    main()
