# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from html import escape
import re

OUTPUT_DIR = Path.cwd()
CTA = "可关注公众号「金赋补贴宝」，通过公众号访问补贴平台，进行企业资质评估和政策匹配，获取更适合自身情况的补贴推荐清单。"

POLICY_ARTICLES = [
    {
        "title": "深圳市工业和信息化局关于印发《深圳市工业和信息化局打造人工智能先锋城市项目扶持计划操作规程（2026年修订版）》的通知",
        "source": "深圳市工业和信息化局",
        "valid_period": "2026年5月1日至2027年6月30日",
        "max_amount": "最高3000万元",
        "article_title": "深圳AI扶持计划升级：哪些企业值得重点关注？",
        "paragraphs": [
            "深圳市工业和信息化局印发《打造人工智能先锋城市项目扶持计划操作规程（2026年修订版）》，政策自2026年5月1日起施行，有效期至2027年6月30日。对深圳AI企业来说，这不是一条单一补贴，而是一套覆盖模型使用、应用落地、开源生态、机器人产品、公共平台和产业活动的组合型扶持计划。",
            "本次扶持计划下设十个项目类别，均采用事后奖补方式。企业可重点关注“模型券”、人工智能行业应用示范标杆、国家“揭榜挂帅”配套、国产人工智能生态源头创新中心、人工智能软件开源奖励、高端展会/论坛/大赛、具身智能机器人产品应用奖励等方向。其中，单个国产人工智能生态源头创新中心每年资助合计最高可达3000万元。",
            "深圳金赋科技有限公司的价值不只是“代找政策”，而是用数据和工具帮企业建立补贴申报判断体系。公司旗下补贴数据平台已收录1100万条全国四级政府公开扶持政策，按产业、区域、资质、项目阶段等维度标签化整理；补贴平台则面向企业提供政策匹配、资质测评、申报清单和时间节点提醒，帮助企业更快判断哪些政策值得投入准备。",
            f"想知道企业是否适合申报本次深圳人工智能扶持计划？{CTA}",
        ],
    },
    {
        "title": "深圳市住房和建设局 深圳市人力资源和社会保障局关于印发《深圳市青年人才住房支持实施办法》的通知",
        "source": "深圳市住房和建设局、深圳市人力资源和社会保障局",
        "valid_period": "2026年1月1日至2031年1月1日",
        "max_amount": "安居补贴最长24个月，每月1250元（税后1000元）",
        "article_title": "深圳青年人才住房支持来了：企业招聘和人才留深都该关注",
        "paragraphs": [
            "《深圳市青年人才住房支持实施办法》自2026年1月1日起施行，有效期5年，核心是解决首次来深青年人才住房需求。政策提供两类支持：一是租住过渡性住房，租金约按市场参考租金60%确定，最长不超过36个月；二是申领安居补贴，每月1250元（税后1000元），发放期不超过24个月，两者不得重复享受。",
            "这项政策看似面向个人，但对企业同样重要。科技型企业、初创企业、专精特新企业和高速成长企业在招聘青年人才时，住房成本往往是影响入职和留任的关键因素。企业如果能及时把人才住房支持信息纳入招聘宣讲、员工入职指引和人力资源服务包，将有助于提升对青年人才的吸引力。",
            "申请条件方面，青年人才应在认定之日起1年内申请住房支持，并通常需要满足未在深圳拥有自有住房、未享受相关住房保障优惠政策、未享受用人单位优惠住房、通过深圳工作单位依法缴纳社保等要求。选择安居补贴的，还需未租住过渡性住房并按规定办理居住登记。",
            "深圳金赋科技有限公司的补贴数据平台不仅关注企业经营类扶持政策，也覆盖人才、住房、社保、创业等公共政策信息。企业可通过补贴平台为员工和候选人快速梳理可享受的政策权益，同时结合企业自身的高新技术企业、专精特新、研发补贴、人才项目等政策，形成更完整的“企业+人才”政策服务方案。",
            f"如果企业希望系统了解员工可享受的人才住房、创业就业、企业补贴等政策，{CTA}",
        ],
    },
    {
        "title": "深圳市发展和改革委员会 深圳市财政局 深圳市商务局关于印发《深圳市超长期特别国债资金支持消费品以旧换新提质增效实施方案（2026年）》的通知",
        "source": "深圳市发展和改革委员会、深圳市财政局、深圳市商务局",
        "valid_period": "2026年2月14日至2026年12月31日",
        "max_amount": "单项补贴最高2万元",
        "article_title": "深圳消费品以旧换新继续加码：商家如何抓住补贴带来的新增量？",
        "paragraphs": [
            "深圳发布2026年消费品以旧换新提质增效实施方案，统筹超长期特别国债资金和市级财政配套资金，重点支持汽车、家电、数码和智能产品等领域。政策目标包括汽车报废更新约3.5万辆、置换更新约18万辆、家电以旧换新约180万件、手机和平板等数码智能产品购新约400万件、智能家居产品购新约150万件。",
            "从补贴标准看，个人消费者购买新能源乘用车报废更新最高补贴2万元，燃油车报废更新最高1.5万元；汽车置换更新中，新能源乘用车最高1.5万元、燃油乘用车最高1.3万元。家电方面，符合条件的1级能效或水效产品按销售价格15%补贴，每件最高1500元；手机、平板、智能手表手环、智能眼镜等单件不超过6000元的产品，按15%补贴，每件最高500元。",
            "对商家来说，这类政策不只是消费者补贴，也会影响门店活动设计、价格备案、产品上架、补贴资格核验、发票和物流数据留存、资金垫付和兑付节奏。方案提出完善参与经营主体名单管理、产品销售价格备案、补贴资格发放、资金审核兑付等全链条机制，并对“支付立享”模式设置预拨付安排，有助于缓解企业垫资压力。",
            "深圳金赋科技有限公司可依托补贴数据平台帮助汽车、家电、数码、智能家居等企业跟踪政策窗口、补贴标准和参与条件；补贴平台可辅助企业快速识别适合自身门店、产品和客户群体的政策机会，并形成活动节点、材料留存和合规提醒清单，降低因信息滞后或资料不完整带来的经营风险。",
            f"如果你是消费电子、家电、智能家居、汽车销售或服务企业，想及时获取以旧换新、促消费、稳增长等政策机会，{CTA}",
        ],
    },
    {
        "title": "市科技创新局 市发展改革委 市市场监管局 市卫生健康委关于印发《深圳市推动合成生物创新引领生物制造产业高质量发展若干措施》的通知",
        "source": "深圳市科技创新局、深圳市发展改革委、深圳市市场监管局、深圳市卫生健康委",
        "valid_period": "2026年4月15日至2029年4月15日",
        "max_amount": "单个项目最高1亿元",
        "article_title": "深圳合成生物政策重磅发布：生物制造企业如何找准申报切口？",
        "paragraphs": [
            "《深圳市推动合成生物创新引领生物制造产业高质量发展若干措施》自2026年4月15日起施行，有效期3年，面向合成生物和生物制造产业提供系统支持。政策覆盖原始创新、技术攻关、企业创新、研发检测、成果转化、合成生物+行动、创新服务载体、产业空间、科技金融、人才培育、产业生态和审批准入等多个环节。",
            "从资金支持看，政策力度较大：市自然科学基金和深医专项单个项目最高1000万元；原创性、引领性技术攻关的揭榜挂帅类项目最高3000万元；涉及重大技术系统、重大工程、重大装备和重大战略的论证类项目最高1亿元；生物制造企业研发费用增长可获得最高300万元资助；人工智能生物制造研发服务合同费用可按15%支持，单个企业每年最高200万元。",
            "适合关注该政策的主体包括合成生物、生物制造、食品农业、医药健康、化妆品、前沿新材料、绿色低碳、关键仪器设备耗材、CRO/CDMO、中试平台、技术转移服务机构等。企业要先判断自己属于研发攻关、产品开发、平台建设、成果转化、产业化落地还是人才和金融支持，再准备对应的研发投入、技术路线、知识产权、检测验证、合作合同和产业化证明材料。",
            "深圳金赋科技有限公司的补贴数据平台已覆盖全国四级公开扶持政策，并按产业领域和申报要素进行标签化管理。对于合成生物和生物制造企业，补贴平台可帮助企业将政策拆解为“可申报方向—资质条件—材料清单—时间窗口—风险点”，避免只看到最高资助金额，却忽略申报主体、费用范围、项目周期和不重复享受等限制。",
            f"生物制造企业如果想系统梳理研发、人才、平台、产业化、科技金融等补贴机会，{CTA}",
        ],
    },
]


def sanitize_windows_filename(name: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', name).strip().rstrip('.')
    return cleaned[:180] or "policy_article"


def paragraph_xml(text: str, style: str | None = None) -> str:
    style_xml = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
    return f"<w:p>{style_xml}<w:r><w:t xml:space=\"preserve\">{escape(text)}</w:t></w:r></w:p>"


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
    generated_docs = []
    for article in POLICY_ARTICLES:
        output_name = sanitize_windows_filename(str(article["title"])) + ".docx"
        output_path = OUTPUT_DIR / output_name
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
    Path("generated_documents.md").write_text(
        "# 生成的Word文档列表\n\n"
        f"{doc_list}\n\n"
        "# 推广文章内容\n\n"
        f"{joined_article_sections}\n",
        encoding="utf-8",
    )
    for output_name, _ in generated_docs:
        print(OUTPUT_DIR / output_name)


if __name__ == "__main__":
    main()
