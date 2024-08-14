import typing as t

if t.TYPE_CHECKING:
    import typing_extensions as te
    from _typeshed import StrPath, SupportsRead

    from mjml.core.api import Component

    class _Output(t.NamedTuple):
        html: str
        errors: t.Sequence[str]

        @te.overload
        def __getitem__(self, _: t.Literal["html"]) -> str: ...
        @te.overload
        def __getitem__(self, _: t.Literal["errors"]) -> t.Sequence[str]: ...
        @te.overload
        def get(self, key: t.Literal["html"], /) -> t.Optional[str]: ...
        @te.overload
        def get(self, key: t.Literal["html"], default: str, /) -> str: ...
        @te.overload
        def get(self, key: t.Literal["errors"], /) -> t.Optional[t.Sequence[str]]: ...
        @te.overload
        def get(self, key: t.Literal["errors"], default: t.Sequence[str], /) -> t.Sequence[str]: ...

    FpOrJson = t.Union[t.Mapping[str, t.Any], str, bytes, SupportsRead[str], SupportsRead[bytes]]

def mjml_to_html(
    xml_fp_or_json: "FpOrJson",
    skeleton: t.Optional[str] = None,
    template_dir: t.Optional["StrPath"] = None,
    custom_components: t.Optional[t.List[t.Type["Component"]]] = None,
) -> "_Output": ...
