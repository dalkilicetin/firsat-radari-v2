"""hipotezler/*.yaml okuyucu."""
import yaml

from mekanizma.ayarlar import HIPOTEZLER


def yukle(ad):
    return yaml.safe_load((HIPOTEZLER / f"{ad}.yaml").read_text(encoding="utf-8"))
