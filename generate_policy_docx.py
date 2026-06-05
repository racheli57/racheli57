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

# 只保留本轮用户新提供的政策链接；此前已生成过的政策不再作为默认输出。
POLICY_URLS = [
    "http://wtl.sz.gov.cn/gkmlpt/content/11/11392/post_11392875.html",
    "https://amr.sz.gov.cn/gkmlpt/content/12/12137/post_12137032.html",
    "http://wtl.sz.gov.cn/gkmlpt/content/11/11165/post_11165855.html",
    "http://wtl.sz.gov.cn/gkmlpt/content/12/12261/post_12261246.html",
    "http://wtl.sz.gov.cn/gkmlpt/content/12/12248/post_12248261.html",
    "https://zjj.sz.gov.cn/gkmlpt/content/11/11274/post_11274386.html",
    "http://wtl.sz.gov.cn/gkmlpt/content/11/11531/post_11531328.html",
    "http://wtl.sz.gov.cn/gkmlpt/content/11/11848/post_11848616.html",
    "https://zjj.sz.gov.cn/gkmlpt/content/12/12057/post_12057501.html",
    "https://amr.sz.gov.cn/gkmlpt/content/11/11115/post_11115025.html",
    "https://zjj.sz.gov.cn/gkmlpt/content/12/12073/post_12073044.html",
    "https://gdii.gd.gov.cn/zwgk/tzgg1011/content/post_4766433.html",
    "https://zxqyj.sz.gov.cn/zwgk/zfxxgkml/zcfg/content/post_11816522.html",
    "https://www.sz.gov.cn/szzt2010/yhyshj/yszc/content/post_12230646.html",
    "https://www.sz.gov.cn/cn/xxgk/zfxxgj/bmdt/content/post_11482362.html",
    "https://www.sz.gov.cn/cn/xxgk/zfxxgj/tzgg/content/post_11906633.html",
    "http://www.lg.gov.cn/xxgk/zwgk/flfg/bmgfxwj/content/post_11321229.html",
    "https://gxj.sz.gov.cn/xxgk/xxgkml/zcfgjzcjd/content/post_11261616.html",
    "http://pnr.sz.gov.cn/gkmlpt/content/11/11285/post_11285366.html#4277",
    "http://www.baoan.gov.cn/kjj/zwgk/lzyj/zcwj/content/post_11007246.html",
    "http://www.yantian.gov.cn/gkmlpt/content/11/11255/post_11255197.html#3863",
    "http://www.szlhq.gov.cn/xxgk/zcfg/qgfxwj/qgfxwj_129575/content/post_10861529.html",
    "http://www.baoan.gov.cn/jjcj/zwgk/zc/zcwj/content/post_11182664.html",
    "http://gxj.sz.gov.cn/gkmlpt/content/11/11241/mpost_11241664.html#3115",
    "https://www.sz.gov.cn/cn/xxgk/zfxxgj/zcfg/content/post_11016662.html",
    "https://www.sz.gov.cn/cn/zjsz/fwts_1_3/tzfw/yhzc_1/content/post_11118772.html",
    "http://gxj.sz.gov.cn/xxgk/xxgkml/zcfgjzcjd/gygh/content/post_11079829.html",
    "http://gxj.sz.gov.cn/gkmlpt/content/11/11210/post_11210745.html#25192",
    "http://gxj.sz.gov.cn/xxgk/xxgkml/zcfgjzcjd/gygh/content/post_11201378.html",
    "https://gxj.sz.gov.cn/gkmlpt/content/11/11203/post_11203635.html#3115",
    "http://qh.sz.gov.cn/sygnan/xxgk/xxgkml/zcfg/zcjd/content/post_4419152.html",
    "http://zjj.sz.gov.cn/csml/zcfg/xxgk/zcfg_1/zcfg/jsgcgl/content/post_8049473.html",
    "http://www.szft.gov.cn/gkmlpt/content/8/8358/post_8358423.html",
    "http://www.dpxq.gov.cn/xxgk/xxgk/zcfg/wj/xqgfxwj/content/post_6845623.html",
    "http://szfb.sz.gov.cn/gkmlpt/content/5/5538/post_5538830.html",
    "http://www.baoan.gov.cn/bahbswj/gkmlpt/content/7/7647/post_7647587.html",
    "http://www.szft.gov.cn/gkmlpt/content/5/5769/post_5769523.html",
    "http://weather.sz.gov.cn/xingxigongkai/zhengcefagui/zcfgson/content/post_3578270.html",
    "http://szfb.sz.gov.cn/gkmlpt/content/5/5535/post_5535274.html",
    "http://tb.sz.gov.cn/ztzl/gfxwjcx/content/post_608487.html",
]

SOURCE_BY_HOST = {
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
    "szfb.sz.gov.cn": "深圳市地方金融管理局",
    "weather.sz.gov.cn": "深圳市气象局",
    "tb.sz.gov.cn": "深圳市交通运输局",
}


PROMOTION_PLANS = [
    ("文旅活动补贴机会：活动办完后，企业还能这样做政策申报", "文化演艺、文创活动、旅游推广和体育运营企业", "活动性质、举办时间、投入费用、参与人数、宣传传播、安全保障和社会效益", "活动方案、合同发票、付款凭证、现场照片、媒体报道、客流数据和复盘报告"),
    ("质量品牌补贴机会：把合规投入变成企业可申报资产", "食品、消费品、检测认证、品牌培育和知识产权相关企业", "质量提升、标准建设、品牌培育、食品安全、知识产权和检验检测要求", "资质证书、检测报告、标准文本、专利商标、合同票据、付款凭证和成果证明"),
    ("旅游服务企业补贴机会：别让运营数据只停留在后台", "旅行社、景区运营、酒店民宿、旅游平台和文旅服务商", "游客服务、产品创新、宣传推广、消费拉动、服务质量和安全管理", "产品方案、订单数据、客户评价、宣传材料、合同发票、人员安排和安全记录"),
    ("体育赛事补贴机会：赛事投入要提前沉淀成申报材料", "体育赛事主办方、场馆运营方、体育培训和体育消费服务企业", "赛事规模、参赛人数、场地保障、市场化投入、宣传效果和公共安全", "赛事方案、场租合同、票据凭证、参赛名单、照片视频、媒体报道和总结报告"),
    ("数字文旅补贴机会：线上流量和线下活动都要形成证据链", "数字文旅平台、内容制作机构、文创企业和文旅科技服务商", "数字化产品、内容传播、平台运营、用户数据、版权归属和场景应用", "软件著作权、平台截图、用户数据、服务合同、发票付款和项目成果说明"),
    ("建筑企业补贴机会：项目台账越完整，政策匹配越高效", "建筑施工、工程咨询、设计监理、园区建设和绿色建筑企业", "项目所在地、建设周期、资质等级、工程质量、绿色低碳和费用投入", "工程合同、验收材料、付款凭证、人员社保、资质证书、信用记录和项目总结"),
    ("演艺文创企业补贴机会：内容项目也能做政策规划", "演艺机构、文创工作室、艺术培训、文化空间和内容制作企业", "原创内容、演出活动、版权保护、市场推广、观众反馈和社会影响", "版权证明、演出合同、票务数据、宣传记录、费用票据、现场照片和复盘资料"),
    ("文旅消费补贴机会：促消费活动要从第一天开始留痕", "商圈、景区、文旅综合体、活动运营商和消费服务平台", "消费拉动、活动主题、商户参与、客流转化、宣传推广和资金使用", "活动方案、商户清单、交易数据、宣传物料、合同发票、付款凭证和效果报告"),
    ("绿色建筑补贴机会：节能低碳项目如何提前准备材料", "绿色建筑、装配式建筑、节能改造、物业和园区运营企业", "绿色认证、节能效果、建设标准、改造投入、验收结果和运营数据", "认证文件、设计方案、改造合同、设备清单、发票付款、能耗数据和验收报告"),
    ("知识产权补贴机会：专利、商标和标准不要只做证书管理", "科技企业、制造业企业、品牌企业、知识产权服务机构和标准参与单位", "知识产权创造、运用、保护、标准制定、品牌培育和质量提升", "专利商标证书、标准文本、服务合同、缴费凭证、转化案例、维权材料和成果说明"),
    ("住建领域补贴机会：住房和物业项目也要有政策意识", "住房服务、物业管理、园区运营、建筑企业和人才住房相关主体", "住房保障、物业服务、项目运营、人才安居、工程质量和信用管理", "项目合同、运营台账、人员资料、费用票据、服务记录、验收材料和信用证明"),
    ("广东制造业补贴机会：省级政策要和深圳项目一起规划", "先进制造、智能制造、绿色制造、专精特新和产业链配套企业", "技术改造、设备更新、数字化转型、产业协同、绿色低碳和创新能力", "设备合同、发票付款、研发台账、知识产权、财务报表、项目成效和验收资料"),
    ("中小企业补贴机会：梯度培育不是拿到称号才开始", "中小企业、创新型企业、专精特新培育企业和服务机构", "企业规模、成长性、研发投入、知识产权、融资情况、管理能力和认定进度", "营业数据、审计报告、研发费用、专利软著、社保人数、荣誉资质和申报计划"),
    ("营商环境政策机会：企业服务事项也能转化为发展红利", "在深经营企业、招商项目、总部企业、创新创业团队和服务机构", "审批便利、服务保障、政策兑现、要素支持、融资服务和企业诉求", "企业基础资料、项目计划、投资证明、经营数据、诉求清单和政策匹配报告"),
    ("企业服务政策机会：从政府动态里发现下一轮补贴窗口", "科技企业、制造业、服务业、外贸企业和创业团队", "部门工作重点、资金方向、产业导向、申报节奏和企业服务安排", "企业画像、资质清单、项目储备、费用台账、政策关注清单和内部责任分工"),
    ("通知公告里的补贴机会：申报时间短，更要提前准备", "近期有项目投入、资质认定、资金申报或政策兑现需求的企业", "受理时间、申报入口、材料要求、审核流程、资金拨付和公示安排", "申请书、营业执照、财务资料、合同发票、付款凭证、项目报告和承诺书"),
    ("龙岗企业补贴机会：区级政策要和市级资质联动", "龙岗区制造业、软件信息、科技服务、专精特新和成长型企业", "区级扶持、企业培育、产业空间、研发投入、技术改造和资质认定", "注册地址证明、营收数据、研发台账、知识产权、项目合同、区级申报材料和市级认定材料"),
    ("工信产业补贴机会：产业项目要从立项时就考虑申报", "工业企业、软件企业、智能制造企业、数字化服务商和产业链企业", "项目建设期、投入金额、设备软件、研发成果、应用场景和产业带动", "立项资料、采购合同、发票付款、设备清单、系统截图、验收报告和绩效证明"),
    ("规划资源政策机会：空间、用地和项目合规也影响补贴", "园区运营、制造业项目、城市更新、产业空间和工程建设主体", "空间用途、规划许可、土地房产、项目选址、建设合规和产业承载", "权属文件、租赁合同、规划资料、项目方案、工程材料和产业落地证明"),
    ("宝安科技企业补贴机会：研发和资质要一起规划", "宝安区科技企业、初创团队、高新技术企业和研发平台", "研发投入、科技成果、创新载体、人才团队、知识产权和产业化进展", "研发费用、专利软著、项目合同、财务资料、人员社保、成果证明和申报书"),
    ("盐田企业补贴机会：特色产业政策要对准自身定位", "盐田区物流、旅游、海洋、商贸、科技和现代服务业企业", "区域产业定位、项目投入、经营贡献、创新能力、服务质量和发展成效", "注册地址、经营数据、合同发票、项目材料、荣誉资质、纳税社保和成果说明"),
    ("龙华企业补贴机会：成长型企业要建立年度申报地图", "龙华区制造业、数字经济、商贸服务、科技企业和园区主体", "区级产业扶持、技术改造、数字化转型、人才服务和企业培育", "企业画像、项目储备、费用台账、知识产权、合同票据、政策日历和责任分工"),
    ("宝安产业补贴机会：经营贡献和项目投入都要留证", "宝安区制造业、商贸服务、外贸、科技和产业园区企业", "产业发展、经营贡献、项目投入、创新能力、市场拓展和稳增长", "营收纳税、合同发票、付款凭证、项目方案、人员社保、荣誉资质和效果报告"),
    ("工信专项补贴机会：专项资金申报不能只看标题", "制造业、软件信息、工业互联网、绿色制造和产业链配套企业", "专项资金方向、支持对象、费用范围、资助比例、项目周期和验收要求", "项目申请书、合同发票、付款凭证、设备清单、研发材料、审计资料和绩效报告"),
    ("市级产业政策机会：跨部门政策要做组合匹配", "深圳各类经营主体，尤其是有研发、技改、人才、市场拓展需求的企业", "市级资金、区级配套、产业导向、资质条件、申报窗口和不重复享受", "企业画像、资质证明、项目台账、财务资料、费用凭证、政策组合表和申报计划"),
    ("投资服务政策机会：招商落地后别忽略补贴兑现", "拟投资深圳、已落地深圳或计划增资扩产的企业", "投资规模、落地时间、产业方向、空间需求、人才团队和经营贡献", "投资协议、工商资料、租赁合同、设备采购、人员社保、纳税证明和项目计划"),
    ("工业规划政策机会：看懂产业方向，提前储备申报项目", "先进制造、软件信息、新材料、智能装备和产业链企业", "产业规划、重点方向、发展目标、项目储备、创新平台和空间布局", "企业战略、项目方案、研发台账、设备投入、知识产权、合作协议和产业化计划"),
    ("工信项目申报机会：材料准备越早，政策兑现越稳", "准备申报工信项目、技改项目、软件项目和数字化项目的企业", "申报条件、建设内容、费用边界、实施周期、验收标准和资金拨付", "申请书、项目报告、采购合同、发票付款、系统截图、验收资料和审计底稿"),
    ("制造业扶持政策机会：把设备和软件投入变成可申报项目", "制造业企业、工业互联网服务商、智能装备和数字化改造企业", "设备更新、软件采购、生产效率、节能降耗、智能化改造和应用成效", "设备清单、软件合同、发票付款、改造前后数据、验收报告和绩效证明"),
    ("工信政策机会：企业要建立可复用的补贴材料库", "工业、软件、信息服务、智能终端和产业链配套企业", "资助类别、项目费用、技术成果、行业应用、市场推广和企业资质", "营业执照、财务报表、合同发票、付款凭证、知识产权、客户案例和项目总结"),
    ("前海政策机会：跨境和现代服务业企业要主动匹配", "前海现代服务业、跨境服务、金融科技、专业服务和创新平台企业", "区域政策、跨境便利、现代服务业、人才支持、办公空间和产业贡献", "注册证明、租赁合同、服务合同、经营数据、人员材料、纳税证明和项目说明"),
    ("建设工程政策机会：工程管理资料也能影响政策申报", "施工、设计、监理、造价咨询、检测和工程管理企业", "工程质量、安全管理、资质等级、项目备案、绿色施工和信用评价", "工程合同、施工资料、验收文件、人员证书、费用凭证、信用记录和项目总结"),
    ("福田企业补贴机会：中心城区政策要看产业定位", "福田区金融、科技、商贸、专业服务和总部经济企业", "总部经济、金融服务、科技创新、商贸消费、楼宇经济和人才支持", "注册地址、租赁合同、营收纳税、人员社保、项目合同、资质证书和发展计划"),
    ("大鹏新区企业补贴机会：生态文旅和特色产业要早做规划", "大鹏新区文旅、海洋、生态农业、民宿、体育和科技服务企业", "生态保护、文旅消费、特色产业、项目投入、品牌推广和经营成效", "项目方案、经营数据、合同票据、宣传资料、安全记录、生态合规和效果报告"),
    ("金融服务补贴机会：融资凭证要和产业项目打通", "科技企业、专精特新企业、拟上市企业和需要融资支持的成长型企业", "贷款贴息、担保补助、上市培育、风险补偿、绿色金融和产业基金", "授信合同、借款合同、利息凭证、担保资料、财务报表、资金用途和项目进展"),
    ("宝安绿色发展补贴机会：环保投入也要形成政策台账", "宝安区制造业、园区运营、环保服务、节能改造和绿色供应链企业", "污染治理、节能降碳、环保设施、绿色改造、监测数据和合规管理", "环保批复、设备合同、监测报告、发票付款、运行台账、能耗数据和验收材料"),
    ("福田经营主体补贴机会：商贸服务企业别错过区级政策", "福田区商贸、专业服务、科技服务、文化消费和楼宇企业", "经营贡献、促消费活动、品牌建设、办公空间、人才服务和产业集聚", "营收纳税、活动方案、合同发票、付款凭证、租赁材料、人员社保和效果报告"),
    ("气象服务政策机会：安全合规资料也可能成为企业资产", "受天气影响较大的建筑、交通、文旅、物流、农业和户外活动企业", "气象安全、防灾减灾、应急预案、风险管理、公共安全和服务保障", "应急预案、培训记录、设施检查、活动方案、安全台账、保险资料和处置记录"),
    ("金融监管政策机会：企业合规融资要提前准备资料", "金融服务机构、类金融企业、融资平台和需要规范融资的企业", "监管要求、合规经营、风险防控、融资服务、信息报送和信用管理", "经营资质、内控制度、合同资料、客户台账、财务报表、风险说明和整改记录"),
    ("交通运输政策机会：物流和出行企业如何做补贴准备", "物流运输、道路客货运、供应链、港航服务和出行服务企业", "运输资质、车辆设备、安全管理、绿色低碳、服务保障和运营数据", "车辆资料、运营台账、安全记录、设备合同、发票付款、能耗数据和服务评价"),
]


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


def remove_urls(text: str) -> str:
    return re.sub(r"https?://\S+", "", text or "").strip()


def fetch_url_text(url: str) -> tuple[str, str]:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=12) as response:
        raw = response.read()
        charset = response.headers.get_content_charset() or "utf-8"
    html = raw.decode(charset, errors="replace")
    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.I | re.S)
    title = strip_html(title_match.group(1)) if title_match else ""
    text = remove_urls(strip_html(html))
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
    return SOURCE_BY_HOST.get(host_from_url(url), "政策发布部门")


def topic_for_source(source: str, url: str) -> tuple[str, str, str]:
    if "文化" in source or "旅游" in source or "体育" in source:
        return (
            "文旅体育政策解读：企业如何把扶持信息变成增长机会？",
            "从文旅体育类政策原文看，企业应重点拆解支持对象、项目类型、活动周期、投入费用、宣传效果、客流或参与数据、安全管理、社会效益和绩效评价等要素。文化演艺、旅游服务、体育赛事、文创活动、数字文旅、场馆运营和公共文化服务主体，不能只关注政策是否提到补贴，更要判断自身项目能否用合同、票据、现场资料、传播数据和用户反馈证明真实投入与实际成效。",
            "深圳金赋服务这类企业时，会先用补贴数据平台匹配市、区两级文旅体育、促消费、品牌活动、赛事展演、数字化改造和经营主体培育政策，再通过补贴平台生成申报优先级、材料清单和时间表。企业可以把一次活动的预算、合同、发票、照片、宣传稿、客流统计和复盘报告统一沉淀，后续遇到同类政策时就能快速判断是否申报，减少临时补材料的压力。",
        )
    if "市场监督" in source:
        return (
            "质量、标准和知识产权政策解读：企业如何把合规能力变成补贴机会？",
            "市场监管类政策原文通常围绕质量提升、标准建设、知识产权、品牌培育、食品安全、计量认证、检验检测、质量奖项或专项资金管理展开。企业需要重点看申报主体、资质证书、项目投入、标准文本、检测报告、专利商标、认证证明、合同发票、付款凭证、项目成果和信用记录等要求。对食品、消费品、制造业、检测机构和平台型企业来说，日常合规资料越完整，后续申报成功率越高。",
            "深圳金赋会把市场监管政策与企业的质量管理、品牌建设、知识产权、标准化、食品安全和检测认证台账结合起来。补贴平台可帮助企业识别适合申报的质量提升、标准研制、知识产权保护、品牌培育和安全追溯类项目，并提醒企业提前补齐证明材料、费用归集和成果说明，让合规投入不只是成本，也能转化为政策资金和品牌背书。",
        )
    if "住房" in source:
        return (
            "住建领域政策解读：建筑和园区企业如何提前做好项目台账？",
            "住建类政策原文往往涉及建筑业、工程管理、住房保障、城市更新、绿色建筑、物业服务、人才住房、工程质量安全或行业规范。企业要重点核验项目所在地、合同主体、建设周期、资质等级、工程资料、验收文件、费用支出、人员社保、信用记录和绩效要求。很多住建政策看似偏管理，但背后常常关系到资质培育、项目备案、奖励补贴、人才安居和绿色低碳专项。",
            "深圳金赋可帮助建筑施工、工程咨询、园区运营、物业服务和住房相关企业，把住建政策与企业资质、项目合同、工程节点、人才政策、绿色建筑、数字化管理和专项补贴进行组合匹配。通过补贴平台，企业可以建立项目级材料清单，提前归档合同、发票、付款、验收、人员和信用资料，避免等申报通知发布后才发现关键文件缺失。",
        )
    if "工业" in source or "中小企业" in source:
        return (
            "工信和中小企业政策解读：企业如何从原文中找到申报路径？",
            "工信和中小企业政策原文通常覆盖技术改造、数字化转型、专精特新、产业集群、软件信息、绿色制造、首版次产品、智能制造、融资服务和企业梯度培育。企业要重点看支持范围、项目建设期、投入下限、资助比例、认定名单、设备和软件费用、研发投入、知识产权、财务数据、合同发票、付款凭证和应用成效。只看最高金额容易误判，真正决定申报价值的是项目与政策条件的匹配度。",
            "深圳金赋的补贴数据平台沉淀1100万条全国四级政策数据，可按区域、行业、营收、研发投入、知识产权、人员规模和项目阶段做标签匹配。补贴平台则帮助企业形成年度申报地图，判断先做专精特新、高新技术、技改补贴、数字化转型、软件项目还是产业专项，并将申报材料拆成企业内部可以执行的SOP。",
        )
    if "金融" in source:
        return (
            "金融支持政策解读：企业如何把融资动作转化为政策支持？",
            "金融类政策原文通常与贷款贴息、融资担保、上市培育、产业基金、绿色金融、风险补偿、金融机构服务实体经济或地方金融监管有关。企业需要重点梳理融资合同、授信文件、利息凭证、担保资料、财务报表、纳税社保、资金用途、项目进展和信用记录。对于成长型企业来说，融资不是孤立动作，应与研发投入、产业项目、资质培育和市场扩张同步规划。",
            "深圳金赋可帮助企业把金融政策与研发补贴、产业扶持、专精特新、人才政策和区级配套联动起来，形成资金规划和申报节奏。补贴平台可提示企业哪些贷款、担保、上市培育或基金项目需要提前留存凭证，哪些政策可以与产业项目形成组合，帮助企业降低融资成本、提高政策资金获取效率。",
        )
    return (
        "政策原文解读：企业如何快速判断是否值得申报？",
        "面对一条新政策，企业首先要从原文中拆出发布部门、适用区域、支持对象、申报时间、资助标准、费用范围、材料要求、审核方式和不重复享受限制。很多企业只看标题或最高金额，容易忽略项目周期、主体资质、合同票据、绩效目标和材料一致性。真正适合申报的政策，必须能落到企业现有资质、项目投入和证明材料上。",
        "深圳金赋科技有限公司依托补贴数据平台沉淀1100万条全国四级公开政策数据，并通过补贴平台提供政策匹配、资质测评、申报清单和节点提醒。企业可以先做一次政策体检，判断这条政策与自身行业、规模、项目阶段和材料基础是否匹配，再决定是否进入正式申报准备，避免盲目投入时间和成本。",
    )

def clean_fetched_title(title: str) -> str:
    title = remove_urls(re.sub(r"\s+", " ", title or "")).strip(" -_|")
    if not title or "$" in title or "function" in title.lower() or len(title) > 80:
        return ""
    for suffix in ("_深圳政府在线", "-深圳政府在线", "_深圳市人民政府门户网站", "-深圳市人民政府门户网站"):
        title = title.replace(suffix, "")
    return title.strip()


def build_article_from_url(url: str, index: int) -> dict[str, object]:
    source = source_from_url(url)
    plan = PROMOTION_PLANS[index - 1] if index - 1 < len(PROMOTION_PLANS) else PROMOTION_PLANS[-1]
    article_title, audience, policy_focus, proof_materials = plan
    fetched_title = ""
    fetched_text = ""
    try:
        fetched_title, fetched_text = fetch_url_text(url)
    except (HTTPError, URLError, TimeoutError, OSError, UnicodeError):
        pass
    policy_title = clean_fetched_title(fetched_title)
    title = policy_title or article_title
    policy_name = f"《{policy_title}》" if policy_title else "这项政策"
    if fetched_text:
        summary = remove_urls(fetched_text[:220])
        opening = f"{policy_name}已经发布，政策来源为{source}。从政策原文来看，企业首先要抓住政策对象、申报条件、支持方式、材料要求和办理节奏等关键信息：{summary}。对想拿补贴的企业来说，政策不是简单通知，而是一份需要拆解成任务清单的行动指南。"
    else:
        opening = f"{policy_name}已经发布，政策来源为{source}。结合该部门政策原文的常见结构，企业首先要核验政策对象、申报条件、支持方式、材料清单、审核流程、资金使用和后续监管要求。对想拿补贴的企业来说，政策不是简单通知，而是一份需要拆解成任务清单的行动指南。"
    paragraphs = [
        opening,
        f"这篇推广文章建议重点面向{audience}。企业阅读政策原文时，不要只看标题和最高金额，而要把{policy_focus}逐项拆开，判断自身是否已经具备申报基础。很多企业项目真实发生、费用也真实支出，却因为没有提前按照政策口径留痕，最后在申报时无法说明项目价值、费用边界和实际成效。",
        f"如果企业准备跟进这类政策，建议从现在开始建立材料台账，重点归集{proof_materials}。同时要检查材料之间的主体名称、项目名称、时间、金额、付款路径和成果描述是否一致。涉及专家评审、专项审计、现场核查或公示的政策，还要提前准备项目背景、实施过程、投入明细、绩效成果和风险说明，避免临近截止才被动补材料。",
        "深圳金赋科技有限公司的核心业务就是运营补贴数据平台和补贴平台，帮助企业更系统地发现补贴、判断补贴、准备补贴并提升申报效率。平台已沉淀全国四级政府公开扶持政策数据，能够按地区、行业、企业规模、资质、研发投入、知识产权、项目费用和时间窗口进行匹配；企业也可以通过政策顾问和服务商生态，获得申报规划、资格评估、材料清单、流程提醒和合规审查支持。",
        "对企业来说，真正有价值的不是看到一条政策，而是知道这条政策是否适合自己、需要补哪些短板、什么时候准备材料、还能不能叠加其他区级、市级、省级或国家级政策。深圳金赋补贴平台可以把政策原文转化为企业视角的申报地图，帮助企业减少信息差和试错成本，把日常经营、研发、市场、人才、融资和合规投入沉淀为可申报的项目资产。",
        f"如果企业希望围绕这条政策判断是否值得申报，并同步发现同区域、同产业、同项目阶段下的其他补贴机会，{CTA}",
    ]
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
            "深圳金赋本身以人工智能和数据应用为技术核心，长期运营补贴数据平台和补贴平台，更理解AI企业在算力、模型、研发和应用示范之间的政策组合关系。平台可帮助企业把算力投入拆解成研发项目、费用台账、申报窗口、材料清单和风险提示，减少因材料口径不一致导致的补正成本。",
        )
    if "会展" in title or "展会" in title:
        return (
            "展会主办方如何提高申报准备效率？",
            "会展类政策的难点在于材料复合度高，既要证明展会真实举办，也要说明专业观众、参展企业、产业带动、宣传效果和费用支出的合理性。主办方需要提前整理合同、发票、付款凭证、现场照片、宣传报道、参展商清单、观众数据和项目总结，避免临近截止才发现证据不足。",
            "深圳金赋可将政策条款拆成可执行清单，帮助会展企业对照申报条件建立费用台账、参展商台账、宣传台账和成果转化台账。依托补贴数据平台，企业还可以继续跟踪商务、文旅、促消费、招商和产业集群类政策，把一次展会补贴申报延伸为长期品牌资产管理。",
        )
    if "专精特新" in title or "企业培育" in title or "单项冠军" in title:
        return (
            "专精特新和成长型企业如何提前布局？",
            "企业培育类政策往往与专精特新、小巨人、单项冠军、高新技术企业、研发投入、知识产权和主导产品市场表现紧密相关。即便部分项目采用免申即享，企业也不能等政策上门，而要提前把研发台账、财务数据、知识产权、质量管理、客户案例和荣誉资质做扎实。",
            "深圳金赋服务企业政策匹配时，会把当下可申报补贴和未来资质培育路径一起看。补贴数据平台可按区域、行业、营收、研发投入、知识产权、社保人数和资质进度进行标签匹配，补贴平台则帮助企业生成年度申报地图，识别先补哪些短板、先准备哪些材料、哪些时间节点必须跟进。",
        )
    return (
        "企业如何快速判断申报价值？",
        "企业面对一条新政策时，首先要判断政策对象、区域范围、申报时间、资助标准、费用范围、材料要求和不重复享受限制。只看最高金额容易误判，真正影响申报结果的是企业资质、项目周期、费用凭证、绩效目标和材料一致性。",
        "深圳金赋科技有限公司依托补贴数据平台沉淀1100万条全国四级公开政策数据，并通过补贴平台提供政策匹配、资质测评、申报清单和节点提醒，帮助企业把政策原文转化为可执行的申报计划。",
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
        output_name = sanitize_windows_filename(str(article["title"])) + ".docx"
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
        "# 推广文章内容\n\n"
        f"{joined_article_sections}\n",
        encoding="utf-8",
    )
    for output_name, _ in generated_docs:
        print(output_dir / output_name)


if __name__ == "__main__":
    main()
