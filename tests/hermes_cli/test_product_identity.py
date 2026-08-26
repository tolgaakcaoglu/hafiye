from hermes_cli import product_identity


def test_hafiye_entrypoint_externalizes_only_user_facing_identity(monkeypatch):
    monkeypatch.setattr(product_identity.sys, "argv", ["/usr/bin/hafiye", "doctor"])
    monkeypatch.delenv("HAFIYE_PACKAGE_ROOT", raising=False)

    assert product_identity.product_name() == "Hafiye"
    assert product_identity.command_name() == "hafiye"
    assert product_identity.externalize("Hermes Agent; run `hermes doctor`") == (
        "Hafiye; run `hafiye doctor`"
    )


def test_hermes_compatibility_entrypoint_keeps_upstream_identity(monkeypatch):
    monkeypatch.setattr(product_identity.sys, "argv", ["hermes", "doctor"])
    monkeypatch.delenv("HAFIYE_PACKAGE_ROOT", raising=False)
    monkeypatch.delenv("HAFIYE_PRODUCT", raising=False)

    assert product_identity.product_name() == "Hermes"
    assert product_identity.command_name() == "hermes"
    assert product_identity.externalize("Hermes Agent; run `hermes doctor`") == (
        "Hermes Agent; run `hermes doctor`"
    )
