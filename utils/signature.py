import xmlsig
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from lxml import etree
from xades import XAdESContext, template, utils
from xades.policy import GenericPolicyId

POLICY_ID = "https://isap.sejm.gov.pl/isap.nsf/download.xsp/WDU20170001802/O/D20171802.pdf"
POLICY_NAME = "w sprawie sposobu przesyłania deklaracji i podań oraz rodzajów podpisu elektronicznego"


class SignedSignatureProperties():
    def __init__(self, city=None, signer="", phone="", email=""):
        # 全部属性均为字符串
        self.city = city
        self.signer = signer
        self.phone = phone
        self.email = email


def sign_xml(xml_data, PFX_PATH, PFX_PASSWORD, properties: SignedSignatureProperties):
    xml = etree.XML(xml_data)
    signature = xmlsig.template.create(
        xmlsig.constants.TransformInclC14N,
        xmlsig.constants.TransformRsaSha256,
        "Signature",
    )
    ref = xmlsig.template.add_reference(
        signature, xmlsig.constants.TransformSha256, uri="", name="REF"
    )
    signature_id = utils.get_unique_id()
    xmlsig.template.add_transform(ref, xmlsig.constants.TransformEnveloped)
    ki = xmlsig.template.ensure_key_info(signature, name="KI")
    data = xmlsig.template.add_x509_data(ki)
    xmlsig.template.x509_data_add_certificate(data)
    serial = xmlsig.template.x509_data_add_issuer_serial(data)
    xmlsig.template.x509_issuer_serial_add_issuer_name(serial)
    xmlsig.template.x509_issuer_serial_add_serial_number(serial)
    xmlsig.template.add_key_value(ki)
    qualifying = template.create_qualifying_properties(
        signature, name=utils.get_unique_id(), etsi='xades'
    )
    props = template.create_signed_properties(qualifying, name=signature_id)
    if properties.signer is not None:
        template.add_claimed_role(props, properties.signer+properties.phone+properties.email)
    if properties.city is not None:
        template.add_production_place(props, city=properties.city)
    policy = GenericPolicyId(
        POLICY_ID,
        POLICY_NAME,
        xmlsig.constants.TransformSha256,
    )
    xml.append(signature)
    with open(PFX_PATH, "rb") as key_file:
        certificate = pkcs12.load_key_and_certificates(key_file.read(), PFX_PASSWORD.encode('utf-8'))
    ctx = XAdESContext(policy)
    ctx.load_pkcs12(certificate)
    ctx.sign(signature)
    signed_xml = etree.ElementTree(xml)
    return etree.tostring(signed_xml, pretty_print=True, xml_declaration=True, encoding="utf-8")


def main(xml_file_path, output_file_path):
    """
    读取 XML 文件，签名后保存为新的 XML 文件。
    :param xml_file_path: 输入 XML 文件路径
    :param output_file_path: 输出 XML 文件路径
    """
    # 签名相关配置
    PFX_PATH = "/Users/chenxi/workspace/python/manifest/Manifest_System/config/Tomek.pfx"
    PFX_PASSWORD = "Kosmos2912!"

    try:
        # 以字节形式读取 XML 文件
        with open(xml_file_path, "rb") as f:  # 改为以二进制模式读取
            xml_data = f.read()

        # 签名 XML 数据
        signed_xml_data = sign_xml(
            xml_data,
            PFX_PATH,
            PFX_PASSWORD,
            SignedSignatureProperties("WARSZAW", "TOMASZ ZABROCKI")
        )

        # 保存签名后的 XML 数据到新文件
        with open(output_file_path, "wb") as f:  # 保存为二进制文件
            f.write(signed_xml_data)

        print(f"签名后的 XML 文件已保存至: {output_file_path}")
    except Exception as e:
        print(f"处理 XML 文件时出错: {e}")


if __name__ == "__main__":
    input_file = "/Users/chenxi/workspace/python/manifest/Manifest_System/config/ZC415HUB.xml"  # 输入 XML 文件路径
    output_file = "/Users/chenxi/workspace/python/manifest/Manifest_System/config/signed_ZC415HUB.xml"  # 输出 XML 文件路径
    main(input_file, output_file)
