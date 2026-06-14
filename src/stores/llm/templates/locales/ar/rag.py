# for prompt ( system , documents(chunks) , footer )
# the idea of the locales that لازم نسخة من هنا يكون ليها مرايا هنا
from string import Template

system_prompt =Template( "\n".join([
    "أنت مساعد مسؤول عن توليد إجابة للمستخدم.",
    "سيتم تزويدك بمجموعة من المستندات المرتبطة باستفسار المستخدم.",
    "يجب عليك توليد الإجابة بالاعتماد فقط على المستندات المقدمة."
]))

document_prompt = Template("\n".join([
    "## رقم المستند: $doc_num",
    "### المحتوى: $chunk_text",
]))

footer_prompt = Template("\n".join([
    "بناءً فقط على المستندات أعلاه، يرجى توليد إجابة للمستخدم.",
    "## الإجابة:",
]))
