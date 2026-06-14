# Data Sovereignty for Black Hills Mining Digital Twin

## Territorial Acknowledgment

He Sapa (the Black Hills) is unceded Lakota territory.

The 1868 Fort Laramie Treaty guaranteed He Sapa to the Oceti Sakowin and their
allies in perpetuity. After Custer's 1874 expedition confirmed the presence of 
gold, the US Congress unilaterally took the Black Hills in 1877. In 
*United States v. Sioux Nation of Indians*, 448 U.S. 371 (1980), the Supreme 
Court ruled this taking unconstitutional under the Fifth Amendment.

The Treaty Nations have declined the offered compensation, now exceeding
$2 billion with interest, maintaining that **The Black Hills are not for sale.**

Every record in this system carries that context as a provenance field.

## Why This Matters for a Mining Dataset
Mining in He Sapa did not happen on neutral land. It happened on 1868 Treaty
Territory, in violation of the US Constitution, following a gold rush triggered
by a US military expedition that itself violated the 1868 treaty.

The environmental consequences of that mining such as tailings, cyanide discharge,
and contaminated streams flow downstream into lands where Lakota Nations live
today. The Cheyenne River drains through the Cheyenne River Sioux Reservation.
The Belle Fourche drains toward Standing Rock. These are not historical facts.
They are present conditions.

Documenting the mining history of He Sapa is therefore also an act of
environmental accountability to the Lakota Nations.

## Governance Frameworks

### OCAP®
The Oceti Sakowin and allied Treaty Nations have Ownership, Control, Access,
and Possession of data describing their territory and resources.

Phase I uses public federal data only. But even public federal data describing
Lakota territory carries OCAP obligations:

- **Ownership**: The information belongs to the Nations whose territory it describes
- **Control**: Results should not be distributed externally without Tribal review
- **Access**: Lakota team members have full access to all Phase I data
- **Possession**: Phase I data currently resides at ESIIL/CU Boulder — temporary

Phase II transition must include transfer of data custody to Lakota-controlled
infrastructure. Reference: https://fnigc.ca/ocap-training/

### CARE Principles

**C : Collective Benefit**: This dataset should benefit the Lakota Nations
who hold rights to He Sapa. It should support environmental accountability,
historical documentation, and Tribal stewardship planning — not further
extraction or dispossession.

**A : Authority to Control**: Lakota Nations have authority over land use
and resource decisions in He Sapa. This analysis is advisory to that
authority, not independent of it. Results should be formally presented
to relevant Lakota governance bodies before external publication.

**R : Responsibility**: Every analytical step is documented and auditable.
The AI extraction pipeline is flagged. The provenance chain from raw federal
data to analysis output is complete and reversible.

**E : Ethics**: The territorial framing uses the Lakota legal and historical
position, not a federal framing. "Unceded territory" is the accurate term.
"Ceded" is not.

Reference: https://www.gida-global.org/care

### FAIR Principles
All Phase I data is from public sources and fully reproducible. Analysis
is exported in open formats (GeoPackage, GeoJSON, CSV, HTML) accessible
with any GIS or data analysis software. Full source citations are included.

Reference: https://www.go-fair.org/fair-principles/

### IEEE 2890-2025
Every record in the gazetteer carries IEEE 2890-2025 provenance fields:
source, steward, license, transformation chain, governance status,
territorial context, AI extraction flag, and human verification status.

Reference: https://standards.ieee.org/ieee/2890/10318/

### Local Contexts TK Notice
All records carry a Traditional Knowledge Notice label. This signals that
Indigenous interests exist in this material and that relevant communities
should be contacted before use.

Phase II: Nation-authorized TK and BC labels will replace the generic
TK Notice once the relevant Lakota Nations have reviewed and authorized them.

Reference: https://localcontexts.org/label/tk-notice/

## Provenance Field

Every record in this system carries the following fields verbatim:

```
treaty_territory : "1868 Fort Laramie Treaty He Sapa (Black Hills)"

treaty_status    : "Unceded Lakota territory. The 1877 Congressional act
                    taking He Sapa was ruled unconstitutional by the US
                    Supreme Court in United States v. Sioux Nation of
                    Indians (1980). The Sioux Nations have declined
                    compensation, maintaining that the land was never
                    legally transferred."

legal_citation   : "United States v. Sioux Nation of Indians, 448 U.S. 371 (1980)"

tk_label         : "TK Notice"
```

The language in `treaty_status` was authored by Lakota team member of this group
and reflects the Lakota legal and historical position, not a federal framing.

## Phase II Proposed Changes
Phase II will add sensitive Tribal data including oral histories, ecological
knowledge, cultural site information, and Tribal-governed environmental
assessments. Every Phase I design decision was made to make Phase II easier:

- Governance fields exist on every record: no retroactive schema migration
- Restricted data tiers are defined: Phase II data slots in without redesign
- Human review queue is established: AI extraction workflow is proven
- Provenance framework is complete: Phase II data inherits it

Before Phase II data is accepted, the following must be in place:

1. Formal data sharing agreement between ESIIL and relevant Treaty Nations
2. Tribal governance body review of Phase I results
3. Ethics review process co-designed with Lakota team members
4. Nation-specific TK/BC label authorization from Local Contexts
5. Transfer plan for data custody to Lakota-controlled infrastructure
6. Restricted access controls for non-public records

## References
- OCAP® Principles: https://fnigc.ca/ocap-training/
- CARE Principles: https://www.gida-global.org/care
- Carroll et al. (2020). The CARE Principles for Indigenous Data Governance.
  *Data Science Journal*, 19(1). https://doi.org/10.5334/dsj-2020-043
- FAIR Principles: https://www.go-fair.org/fair-principles/
- IEEE 2890-2025: https://standards.ieee.org/ieee/2890/10318/
- Local Contexts TK Notice: https://localcontexts.org/label/tk-notice/
- *United States v. Sioux Nation of Indians*, 448 U.S. 371 (1980):
  https://supreme.justia.com/cases/federal/us/448/371/
