from django.utils.translation import gettext_lazy as _
from django.db import models


class Sector(models.TextChoices):
    SAAS = "SaaS", _("SaaS")
    FINTECH = "Fintech", _("Fintech")
    BIOTECH = "Biotech", _("Biotech")
    ECOMMERCE = "E-commerce", _("E-commerce")
    HEALTHCARE = "Healthcare", _("Healthcare")
    EDTECH = "EdTech", _("EdTech")
    AI_ML = "AI/ML", _("AI/ML")
    OTHER = "Other", _("Other")


class SubSector(models.TextChoices):
    B2B = "B2B", _("B2B")
    B2C = "B2C", _("B2C")
    DEFI = "DeFi", _("DeFi")
    INSURTECH = "InsurTech", _("InsurTech")
    TELEMEDICINE = "Telemedicine", _("Telemedicine")
    MARKETPLACE = "Marketplace", _("Marketplace")
    OTHER = "Other", _("Other")
