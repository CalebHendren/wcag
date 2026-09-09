# Laws and policies: which standard each one points at

This file orients an audit toward the right version and level. It is not legal advice, and
deadlines move. When a date affects a decision, check the current text of the rule with the
issuing authority before relying on it, and say in the report which source and date you
used.

The practical shortcut: almost every regime below lands on WCAG Level AA. Audit against
WCAG 2.2 Level AA by default. WCAG 2.2 is backward compatible with 2.1 and 2.0, so a 2.2 AA
pass satisfies an obligation written against 2.1 AA, while the reverse is not true.

## United States

**ADA Title II (state and local government).** The Department of Justice published a final
rule in April 2024 setting WCAG 2.1 Level AA as the technical standard for web content and
mobile apps of state and local government entities. It covers web pages, mobile
applications, electronic documents such as PDFs, and multimedia. In April 2026 the DOJ
issued an interim final rule extending the original compliance dates by one year. As
published, entities serving populations of 50,000 or more have until 26 April 2027, and
smaller entities and special district governments until 26 April 2028. Confirm the current
dates at ada.gov before citing them.

**ADA Titles I and III (employment, public accommodations).** No technical standard is
codified. Courts and settlements have consistently treated WCAG 2.0 or 2.1 Level AA as the
benchmark, so audit to AA and say that the standard is not statutory.

**Section 508 (federal agencies and contractors).** The Revised 508 Standards incorporate
WCAG 2.0 Level A and AA by reference and apply them to web content, electronic documents,
and software. Procurement usually asks for an ACR based on the VPAT template.

**Section 504.** Rules issued by the Department of Health and Human Services and the
Department of Education in 2024 set WCAG 2.1 Level AA for recipients of federal financial
assistance in their respective sectors, with their own compliance schedules.

**State laws.** Several states impose their own requirements on state agencies and, in some
cases, on private entities. Check the specific state when the target is a state government
service.

## European Union

**European Accessibility Act, Directive (EU) 2019/882.** Requirements applied from 28 June
2025 to products and services placed on the market or provided after that date, with
transitional provisions running to 2030 for some service contracts and self-service
terminals. It reaches private-sector services including e-commerce, banking, e-books,
transport, and telecoms. Member states transposed it into national law, so the enforcement
detail is national.

**Web Accessibility Directive, Directive (EU) 2016/2102.** Public sector bodies' websites
and mobile apps, with an accessibility statement and a feedback mechanism required.

**EN 301 549.** The harmonized European standard that both directives lean on. Version
3.2.1, published in March 2021, references WCAG 2.1 Level AA and adds requirements beyond
WCAG for non-web documents, non-web software, hardware, support services, and an
accessibility statement. A later version aligning with WCAG 2.2 has been in preparation.
Check the current published version at the ETSI portal.

EN 301 549 matters for an audit because it covers ground WCAG does not: Clause 5 generic
requirements, Clause 6 two-way voice and video, Clause 8 hardware, Clause 11 software
including native mobile apps, Clause 12 documentation and support, and Clause 13 relay and
emergency services. A "WCAG AA" audit alone does not establish EN 301 549 conformance.

## United Kingdom

The Equality Act 2010 creates a general duty to make reasonable adjustments. The Public
Sector Bodies (Websites and Mobile Applications) Accessibility Regulations 2018 require
public sector bodies to meet an accessibility standard and to publish an accessibility
statement.

## Canada

The Accessible Canada Act applies to federally regulated entities. Ontario's AODA
Information and Communications Standards required WCAG 2.0 Level AA for designated
organizations, excluding live captions and pre-recorded audio description. Other provinces
have their own statutes.

## Australia

The Disability Discrimination Act 1992 creates the underlying obligation, and Australian
government digital policy has required WCAG Level AA for government services.

## What this means for the report

State the target standard as a version and a level, not as a law. Write "WCAG 2.2 Level AA"
in the scope section, and mention the driving obligation separately:

> Tested against WCAG 2.2 Level AA. The client's stated obligation is ADA Title II, which
> the DOJ rule sets at WCAG 2.1 Level AA. Testing at 2.2 covers that obligation and
> identifies the nine criteria added in 2.2 separately.

When an obligation reaches beyond WCAG, as EN 301 549 and Section 508 both do, say which
clauses were outside the scope of the audit rather than implying the audit covered them.
