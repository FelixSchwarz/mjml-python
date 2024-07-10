import pathlib
import typing as t

if t.TYPE_CHECKING:
    from _typeshed import SupportsRead

    from mjml.core.api import Component

    class _Output(t.NamedTuple):
        html: str
        errors: t.Sequence[str]

    FpOrJson = t.Union[t.Dict[str, t.Any], str, bytes, SupportsRead[str], SupportsRead[bytes]]
    StrOrPath = t.Union[str, pathlib.PurePath]

def mjml_to_html(
    xml_fp_or_json: "FpOrJson",
    skeleton: t.Optional[str] = None,
    template_dir: t.Optional["StrOrPath"] = None,
    custom_components: t.Optional[t.List[t.Type["Component"]]] = None,
) -> "_Output": ...
