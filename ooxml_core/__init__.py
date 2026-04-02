"""ooxml_core — shared OOXML utilities for Office document manipulation.

Public API:
    from ooxml_core import pack, unpack, validate, repair, soffice, cjk_utils
    from ooxml_core.pack import pack
    from ooxml_core.unpack import unpack
    from ooxml_core.validate import validate
    from ooxml_core.repair import repair
    from ooxml_core.soffice import run_soffice
    from ooxml_core.cjk_utils import (
        get_display_width, inject_korean_lang, inject_korean_lang_word,
        inject_cjk_fonts, check_contrast, estimate_text_width_inches,
    )
"""

from ooxml_core.pack import pack
from ooxml_core.unpack import unpack
from ooxml_core.validate import validate
from ooxml_core.repair import repair
from ooxml_core.soffice import run_soffice
from ooxml_core.cjk_utils import (
    get_display_width,
    inject_korean_lang,
    inject_korean_lang_word,
    inject_cjk_fonts,
    check_contrast,
    estimate_text_width_inches,
)

__all__ = [
    "pack",
    "unpack",
    "validate",
    "repair",
    "run_soffice",
    "get_display_width",
    "inject_korean_lang",
    "inject_korean_lang_word",
    "inject_cjk_fonts",
    "check_contrast",
    "estimate_text_width_inches",
]
