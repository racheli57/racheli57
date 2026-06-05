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


class HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if text:
            self.parts.append(text)

    def get_text(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self.parts)).strip()


def strip_html(raw_html: str) -> str:
    parser = HTMLTextExtractor()
    parser.feed(unescape(raw_html or ""))
    return parser.get_text()


def fetch_url_text(url: str) -> tuple[str, str]:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=12) as response:
        raw = response.read()
        charset = response.headers.get_content_charset() or "utf-8"
    html = raw.decode(charset, errors="replace")
    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.I | re.S)
    title = strip_html(title_match.group(1)) if title_match else ""
    text = strip_html(html)
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
            "文旅体育企业如何把政策信息转化为增长机会？",
            "这类政策通常关系到文化产业、旅游服务、体育赛事、文创活动、公共文化服务或行业规范。企业需要重点关注支持对象、项目发生时间、活动场地、合同票据、宣传成效、客流数据、安全合规和绩效材料，不能只在看到申报通知后才临时整理。",
            "深圳金赋可帮助文旅体育企业把政策拆成可执行清单，结合补贴数据平台沉淀的政策标签，梳理文旅消费、品牌活动、赛事展演、数字文旅、宣传推广和经营主体培育等机会。",
        )
    if "市场监督" in source:
        return (
            "质量、标准和知识产权政策如何变成企业竞争力？",
            "市场监管类政策往往涉及质量提升、标准建设、知识产权、品牌培育、食品安全、计量认证、检验检测或专项资金管理。企业应提前留存资质证书、检测报告、标准文本、知识产权证明、合同发票、付款凭证和项目成果，形成可核验的合规证据链。",
            "深圳金赋可将市场监管政策与企业的品牌、认证、标准、专利、质量管理和食品安全台账结合起来，帮助企业判断哪些项目适合申报、哪些材料需要提前补齐。",
        )
    if "住房" in source:
        return (
            "住建领域政策发布后，企业应如何做项目台账？",
            "住建类政策常涉及建筑业、工程管理、住房保障、城市更新、绿色建筑、物业服务或人才住房等事项。企业要重点核验项目所在地、合同主体、建设周期、资质等级、工程资料、费用支出、验收文件和信用记录，避免因台账不完整影响后续申报或备案。",
            "深圳金赋可帮助建筑、工程、园区和住房相关企业，把住建政策与资质培育、项目管理、人才住房、绿色低碳和专项补贴进行组合匹配。",
        )
    if "工业" in source or "中小企业" in source:
        return (
            "制造业和中小企业如何从政策中找到申报路径？",
            "工信和中小企业政策通常覆盖技术改造、数字化转型、专精特新、产业集群、软件信息、绿色制造、首版次产品和企业梯度培育。企业应提前准备研发投入、设备购置、知识产权、财务数据、项目合同、发票付款、应用成效和资质证明。",
            "深圳金赋可依托补贴数据平台为制造业和中小企业生成年度申报地图，帮助企业判断先做专精特新、高新技术、技改补贴、软件项目还是产业专项。",
        )
    if "金融" in source:
        return (
            "金融支持政策如何服务企业融资和发展？",
            "金融类政策往往与贷款贴息、融资担保、上市培育、产业基金、绿色金融、风险补偿或金融机构服务实体经济相关。企业需要梳理融资合同、授信资料、利息凭证、财务报表、纳税社保、项目用途和信用记录，提前判断政策适配度。",
            "深圳金赋可帮助企业把金融政策与研发补贴、产业扶持、专精特新和人才政策联动起来，形成资金规划和申报节奏。",
        )
    return (
        "企业如何快速判断这条政策是否值得跟进？",
        "面对新政策，企业首先要判断发布部门、适用区域、支持对象、申报时间、资助标准、费用范围、材料要求和不重复享受限制。只看标题容易误判，真正影响申报结果的是企业资质、项目周期、费用凭证、绩效目标和材料一致性。",
        "深圳金赋可把政策原文转化为企业可执行的申报计划，帮助企业从海量政策中快速筛选值得投入准备的项目。",
    )


def build_article_from_url(url: str, index: int) -> dict[str, object]:
    source = source_from_url(url)
    fallback_title = f"{source}政策链接{index}（{post_id_from_url(url)}）"
    fetched_title = ""
    fetched_text = ""
    try:
        fetched_title, fetched_text = fetch_url_text(url)
    except (HTTPError, URLError, TimeoutError, OSError, UnicodeError):
        pass
    title = fetched_title or fallback_title
    article_suffix, target_guidance, jinfu_guidance = topic_for_source(source, url)
    summary = fetched_text[:180] if fetched_text else f"该链接来源于{source}，建议企业结合原文进一步核验政策对象、申报条件、材料清单和时间节点。"
    paragraphs = [
        f"{title}。这条政策来源于{source}，原文链接为：{url}。从政策信息管理角度看，企业不应只把它当作通知收藏，而应尽快把政策要点拆解为适用对象、申报窗口、资助方式、材料要求和内部责任人。政策原文摘要可先关注：{summary}",
        target_guidance,
        "很多企业错过政策红利，不是因为完全不符合条件，而是没有在政策发布后及时做匹配和资料归集。建议企业先核验注册地、行业方向、项目实施地、资质证书、合同发票、付款凭证、项目成果、信用记录、纳税社保和历史申报情况，再判断是否需要进入正式申报准备。",
        jinfu_guidance,
        f"如果你希望针对这条政策做企业资质评估，并同步发现同区域、同产业、同项目阶段下的其他补贴机会，{CTA}",
    ]
    return {
        "title": title,
        "source": source,
        "valid_period": "以政策原文及后续申报指南为准",
        "max_amount": "以政策原文及后续申报指南为准",
        "from_url": url,
        "article_title": article_suffix,
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
        from_url = article.get("from_url")
        url_line = f"- 政策链接：{from_url}\n" if from_url else ""
        article_sections.append(
            f"## 政策{index}：{article['title']}\n\n"
            f"- Word文件：`{output_name}`\n"
            f"- 政策来源：{article['source']}\n"
            f"{url_line}"
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
