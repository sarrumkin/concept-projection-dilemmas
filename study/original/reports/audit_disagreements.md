# Сопоставление AI-аудитов

После дополнительной сверки кодирования аудит 1 выбирает авторский B в 229/240, аудит 2 — в 236/240. Оба выбрали B в 225/240; нормализованные ответы совпали в 225/240. Первые ответы: 154, 221 и 140 соответственно. Корпус и основные240 отношений не редактировались.

Эти доли — согласие AI-процедуры с автором, не точность относительно независимой истины. Дополнительная сверка включала чтение смысла и выявила ошибки пересказа; её нельзя свести к чисто техническому исправлению. Все первоначальные объяснения сохранены, даже когда они ошибочно описывают кандидата. Один неразрешённый ответ сохраняется в соответствии с процедурой; он не удаляется из основной оценки.

## Распределения итоговых ответов

- Аудит 1: {'B': 229, 'C': 10, 'neither': 1}; нормализация X/Y в B/C использует скрытый от аудиторов ключ.
- Аудит 2: {'B': 236, 'C': 4}; нормализация X/Y в B/C использует скрытый от аудиторов ключ.

## Все случаи без совместного выбора B

### e149232 — personal_gain_vs_collective_impact / arts

**A:** A sculptor can triple her commission by producing a corporate installation from newly quarried marble instead of reclaimed stone. The fresh material will increase her earnings and simplify fabrication, but extraction scars a protected landscape and transport creates substantial emissions. Should she accept the lucrative material choice or earn less while reducing those wider costs?

**B:** A takeaway owner can boost his margin by serving every meal in inexpensive layered packaging. Customers like its convenience, but the containers cannot be recycled and thousands would enter local rubbish each month. Should he adopt the profitable packaging or accept lower earnings to reduce the waste spread through the community?

**C:** A cellist wants to master a difficult concerto by practicing before breakfast for the next eight months. Remaining in bed offers immediate warmth and rest, and no performance is scheduled, but skipped mornings will postpone the skill she wants. Should she maintain the demanding practice habit or choose the comfort of sleeping later?

**Аудит 1: C (X), high.** Both pit a demanding future-oriented practice against immediate comfort and rest that make postponement attractive.

Примечание сверки: Only X expresses demanding future-oriented practice versus immediate comfort; Y concerns profit versus waste.

**Аудит 2: B (X), high.** Both compare personal financial gain from resource-intensive choices with environmental damage and costs spread across communities.

---

### e224123 — fairness_vs_mercy / agriculture

**A:** A dairy cooperative reduces every member’s payment when milk arrives above the agreed temperature, and four farms were penalized this month. Grace’s cooling unit failed during a lightning strike minutes before collection, leaving her family unable to cover wages if penalized. Should the board excuse her loss or apply the common standard?

**B:** A clinic cancels appointments after two late arrivals so waiting times remain equal, and several patients have already been removed. Mr. Bell arrives late again because his wheelchair lift jammed, but missing today delays essential wound care. Should the receptionist make an exception for him or follow the rule enforced on others?

**C:** A landowner can earn a large fee by leasing a hillside to a company for intensive lavender production. The irrigation would lower a shared aquifer and leave dozens of downstream households with weaker wells during summer. Should she take the private income or reject the lease because of its dispersed cost to others?

**Аудит 1: C (Y), high.** Both weigh private income against dispersed environmental costs imposed on shared resources and surrounding households.

**Аудит 2: B (X), high.** Both weigh consistent enforcement of a shared standard against excusing an individual whose hardship or accident caused the violation.

---

### e239295 — fairness_vs_mercy / arts

**A:** A dance academy bars students from the annual performance after more than four absences. Director Opal knows one talented dancer missed five rehearsals while moving between foster homes and sees how much the performance matters to her, while other students met the requirement. Should Opal let the dancer perform or apply the attendance rule equally?

**B:** A software conference refunds no tickets within seven days of opening. Organizer Dae receives a request from a freelancer whose premature baby requires unexpected hospital care; the ticket cost would help him travel to the child, although other late cancellations received nothing. Should Dae issue a compassionate refund or uphold the same policy for all attendees?

**C:** Sculptor Ines saved her commission payment to replace unsafe wiring in her studio before winter. A neighboring artist's dog is struck by a car and needs surgery tonight, but using the savings would leave Ines working around a serious electrical risk. Should Ines pay for the dog's treatment or keep the money for her own safety?

**Аудит 1: B (X), high.** Both weigh consistent attendance or refund rules against compassionate exceptions for people facing exceptional personal crises.

Примечание сверки: Only X expresses a consistent refund rule versus a hardship exception; Y concerns financial security versus aid.

**Аудит 2: C (X), high.** Both ask whether to apply a uniform attendance or cancellation rule despite compelling hardship, or grant compassionate relief.

---

### e372525 — fairness_vs_mercy / public_services

**A:** Emergency housing is assigned strictly by the date each application was completed. A family whose apartment burned down yesterday asks to move ahead of twelve households already waiting in temporary rooms. Advancing them would respond to sudden hardship but violate the same queue used for everyone. Should the housing officer move the family forward?

**B:** A farming cooperative limits every member to a five-thousand-dollar emergency loan. One farmer needs twice that amount after cancer treatment left him unable to plant, while others with severe losses received only the standard sum. Should the board grant him a larger loan because of his illness?

**C:** A librarian has saved enough leave to cover her income if her chronic back condition flares again. A homeless patron she knows needs someone to pay a week's hostel fee before winter beds fill. Helping him would provide immediate shelter but leave her financially exposed during her next absence. Should she pay the fee?

**Аудит 1: neither (neither), medium.** A centers queue fairness under sudden hardship, while X and Y concern personal financial aid and loan limits rather than the same rule conflict.

**Аудит 2: B (Y), high.** Both weigh consistent application of an established allocation rule against making a compassionate exception for severe individual hardship.

---

### e385608 — privacy_vs_openness / agriculture

**A:** A cooperative asks each farmer to explain personal debts before voting on a shared equipment loan. Daniel's recent bankruptcy would clarify why he opposes the terms and might build trust, but even his relatives do not know about it. Should he reveal his financial history to the group or preserve his privacy and leave his vote unexplained?

**B:** A fire chief returns after several unexplained absences, and her crew doubts whether she can cover emergencies. Telling them she was caring for a brother with addiction could rebuild trust and improve shift planning, but would expose painful family information. Should she explain the absences openly or keep her brother's circumstances private?

**C:** A grower can increase his income by covering fifty hectares with inexpensive plastic mulch each season. It raises yields and simplifies weeding, but fragments remain in the soil, wash into streams, and burden neighboring land long after harvest. Should he use the profitable plastic or accept lower earnings to reduce the widespread environmental damage?

**Аудит 1: C (X), high.** Both offer private economic gain through a convenient practice that creates persistent, widespread environmental costs for others.

Примечание сверки: Only X expresses private economic gain versus widespread environmental costs; Y concerns disclosure and privacy.

**Аудит 2: B (Y), high.** Both weigh revealing sensitive personal circumstances to improve trust and coordination against preserving privacy for oneself or family.

---

### e393194 — fairness_vs_mercy / small_business

**A:** A laundromat charges the same replacement fee whenever customers lose a machine key. Owner Hamid meets an elderly customer who lost hers during an emergency evacuation and cannot afford both the fee and groceries, though everyone else has paid. Should Hamid replace her key without charge or follow the stated rule for every customer?

**B:** The housing office grants extensions only when repair applications arrive before a fixed cutoff. Clerk Sarah receives a late form from a tenant who was hospitalized and now faces a winter without heat, while several other late applicants were denied. Should Sarah accept his application because of the hardship or enforce the deadline consistently?

**C:** Bicycle shop owner Lian can stock an innovative folding bike from a new maker whose design might attract adventurous commuters but has little reliability history. A proven model sells steadily and includes dependable replacement parts, though it offers customers nothing new. Should Lian take a chance on the experimental bicycle or order the predictable established model?

**Аудит 1: B (Y), high.** Both weigh applying a fixed deadline or fee consistently against granting a compassionate exception for someone facing severe hardship.

**Аудит 2: C (X), high.** Both contrast an uncertain new option with a dependable established alternative, while the decision carries wider public consequences.

Примечание сверки: Y is the equal-rule versus hardship case described; X is uncertainty versus reliability.

---

### e460139 — autonomy_vs_approval / public_services

**A:** A newly appointed librarian wants to replace formal silence rules with conversational study zones. Her family, senior staff, and longtime patrons expect her to preserve the strict atmosphere and warn that they will oppose her leadership. Should she implement the library she believes residents need or keep the old rules to retain their approval?

**B:** A composer wants her commissioned memorial piece to include street sounds recorded near the deceased artist's home. The orchestra and the artist's family expect a conventional string work and may reject anything else. Should she follow her own artistic judgment or write the traditional music that would secure their acceptance?

**C:** A transit director can receive a substantial bonus by signing a contract for cheap diesel buses before year-end. The deal improves his personal finances, but the fleet would emit more pollution across crowded neighborhoods for a decade. Should he take the rewarded contract or forgo the bonus to reduce the diffuse harm to residents?

**Аудит 1: C (X), high.** Both offer private or professional benefit through choices that impose broad pollution or approval-related costs on others.

**Аудит 2: B (X), high.** Both contrast implementing personally preferred work against conforming to family, staff, or patrons’ expectations for approval.

---

### e541035 — health_vs_duty / arts

**A:** Stage manager Ruth promised to call every cue for her community theater's opening night, and no understudy knows the complicated lighting sequence. Hours before curtain she experiences chest pain and is advised to seek immediate evaluation; canceling disappoints a sold-out audience, while continuing could endanger her health. Should Ruth go to the hospital or fulfill her opening-night responsibility?

**B:** Cafe owner Ben has bronchitis and his doctor prescribed two days of complete rest. His only employee calls out just before a prepaid memorial reception, leaving the grieving family without the meal Ben agreed to provide. Should Ben open the kitchen and honor the booking or close the cafe to protect his recovery?

**C:** A gallery charges every exhibitor the same late fee when work arrives after the installation deadline. Curator Mina's former teacher misses it because she has been caring for her terminally ill husband and cannot afford the charge, though others have paid after difficult weeks. Should Mina waive the fee for her teacher or enforce the rule equally?

**Аудит 1: C (X), high.** Both weigh enforcing a fixed fee rule against granting a compassionate exception for someone facing extraordinary personal hardship.

**Аудит 2: B (Y), high.** Both pit fulfilling a significant commitment serving others against stopping for urgent personal health protection.

---

### e660306 — quality_vs_speed / software

**A:** A nonprofit needs its donation app ready before a televised fundraiser on Sunday. Programmer Joel can launch the core payment flow after a brief test, capturing that audience, or postpone release to examine accessibility, refunds, and unusual card failures carefully. Should Joel ship the usable app before the fundraiser or delay it until the full experience is reliable?

**B:** A stadium's running track must reopen for school championships next week. Contractor Laila can apply one quick surface coat and meet the date, or add two carefully cured layers that provide better grip and durability but force organizers to reschedule. Should Laila finish the track quickly for the championships or delay reopening for higher-quality work?

**C:** A video platform offers developer Marco a large bonus to add automatic high-resolution playback as the default. The feature would increase subscriptions and his payout, but it would consume more electricity and network capacity for millions of viewers who never requested it. Should Marco pursue the bonus by enabling the feature or keep efficient playback to reduce the shared resource cost?

**Аудит 1: B (X), high.** Both balance releasing a usable product quickly against delaying for accessibility, testing, and dependable quality.

**Аудит 2: C (Y), high.** Both weigh releasing a minimally tested product on schedule against delaying for careful validation and dependable performance.

---

### e661245 — security_vs_care / arts

**A:** Sofia has set aside her final three hundred dollars to insure the camera she uses for paid wedding photography. Her neighbor's violin was damaged in a basement flood, and without money for repairs he will lose a confirmed orchestra audition. Helping him would leave Sofia's livelihood exposed to theft. Should Sofia pay for the repair?

**B:** Caleb keeps a reserve fund for veterinary bills and winter feed on his small goat farm. A nearby farmer has broken her leg and needs immediate money to hire someone to milk her herd before the animals become sick. Covering that cost would leave Caleb unprepared for trouble on his own farm. Should he help her?

**C:** The director of a century-old theater can replace its annual live pantomime with an interactive digital production that lets remote audiences influence the ending. The experiment may attract younger viewers, but local families and retired performers treasure the familiar songs, costumes, and shared holiday ritual. Should the theater adopt the new format?

**Аудит 1: C (X), high.** Both contrast modernization of inherited rituals with preserving communal identity, though Y also shares scarce-resource aid stakes.

Примечание сверки: Only X expresses modernization of an inherited communal ritual; Y concerns scarce resources versus aid.

**Аудит 2: B (Y), high.** Both balance protecting a limited personal reserve needed for one’s livelihood against urgently helping another person or household.

---

### e671952 — fairness_vs_mercy / science

**A:** A research institute removes anyone who misses two mandatory safety trainings from laboratory access. One technician missed the second session while caring for his wife during chemotherapy and asks to remain until the next course. Others lost access under the same rule. Should the director suspend him equally or grant an exception for his hardship?

**B:** A coding boot camp refunds tuition only when students withdraw during the first week. One participant asks for a late refund after becoming the sole carer for an injured parent, though earlier withdrawals received nothing. Returning her money would help with rent but break the known policy. Should the school enforce the deadline or show her mercy?

**C:** A planetary scientist is offered leadership of a celebrated observatory on another continent. The role would crown years of research and open major projects, but her partner cannot move and she would leave the close lab group that gathers at her home every week. Should she pursue the directorship or remain with the people who anchor her life?

**Аудит 1: C (Y), high.** Both pit a prestigious leadership opportunity requiring separation against remaining with close relationships that anchor daily life.

**Аудит 2: B (Y), high.** Both weigh applying a known eligibility rule equally against granting an exception for serious personal hardship.

---

### e675540 — security_vs_care / agriculture

**A:** A dairy farmer has stored enough feed to carry his herd through a forecast dry month. His neighbor's injured horse has gone without proper hay, and she cannot buy more until insurance pays. Sharing the feed would relieve the animal now but could leave his own cattle short. Should the farmer keep his full reserve or give her several bales?

**B:** Residents saved donations to repair the roof of their volunteer hall before autumn storms. A longtime volunteer needs a wheelchair ramp at home after an accident, and no public grant will arrive for months. Redirecting the fund would postpone the roof and risk water damage. Should the committee protect the hall budget or build the ramp for him now?

**C:** A young farmer can plant an unfamiliar heritage grain that may command a premium and reveal which crops suit the changing climate. Her insurer will cover only the standard wheat with predictable yields, which would protect the farm if summer turns harsh. Should she experiment with the untested grain or choose the insured crop and a safer harvest?

**Аудит 1: C (Y), medium.** Both contrast uncertain experimentation with a protected predictable option, balancing innovation and upside against insurance and safety.

**Аудит 2: B (Y), high.** Both balance protecting one’s own essential reserve or institution against helping another person with an urgent practical need.

---

### e687961 — autonomy_vs_approval / software

**A:** Niko wants to build accessibility tools at a small software cooperative, where the work matches his interests and the pay is adequate. His former classmates expect him to join a famous technology firm and have already congratulated him on applying there. Choosing the cooperative could cost their admiration. Which offer should Niko accept?

**B:** After residency, Zoe wants to practice family medicine in a coastal village. Her supervising physicians and relatives push her toward cardiology at a prominent urban hospital, a choice they would respect and proudly announce. The village work feels more personally meaningful but less prestigious to them. Which career should Zoe pursue?

**C:** A coding bootcamp refunds tuition only to students who attend at least ninety percent of sessions, a published rule applied to everyone last term. Omar falls one class short because he accompanied his frightened mother to chemotherapy. Should the director grant his refund because of that hardship or enforce the attendance threshold equally?

**Аудит 1: B (Y), high.** Both ask whether to follow personally meaningful work despite family or peers expecting a prestigious path and offering approval.

**Аудит 2: C (Y), high.** Both contrast personally meaningful career choices with prestigious alternatives favored by family and peers for status and approval.

---

### e760826 — health_vs_duty / software

**A:** Ravi promised to monitor a client’s overnight software migration because his teammate is attending a funeral. By midnight, a severe migraine makes the screen painful and concentration difficult, yet leaving could strand the client if the database fails. Should Ravi hand off the responsibility and rest, or remain online until the migration finishes?

**B:** Elise agreed months ago to supervise neighboring farms’ irrigation while their owners attend a regional meeting. A stomach illness now leaves her weak and dehydrated, but an unusually hot afternoon could ruin young crops if nobody adjusts the valves. Should she recover at home or fulfill the commitment despite feeling ill?

**C:** A developer discovers that his close friend quietly copied proprietary code into the startup they built together. An investor asks directly whether every component was written or properly licensed. Telling the truth could expose his friend to dismissal and legal claims; denying the problem protects him but misleads the investor. How should the developer answer?

**Аудит 1: C (X), high.** Both weigh truthfully reporting misconduct that harms a trusted relationship against protecting that person through concealment or deception.

**Аудит 2: B (Y), high.** Both pit honoring a critical professional commitment despite illness against handing over duties to protect personal recovery.

---

### e793029 — freedom_vs_safety / healthcare

**A:** After standard therapies fail, patient coordinator Lena can enroll Mr. Harris in a new trial whose benefits and side effects remain uncertain. A conventional treatment is unlikely to cure him but has a well-known course and can reliably control symptoms for months. Should Lena encourage the experimental possibility or recommend the predictable treatment plan?

**B:** Runner Keisha has qualified for a trail race where competitors choose their own route between mountain checkpoints, offering adventure but uncertain terrain and finish times. A road race that weekend follows closed streets, staffed aid stations, and a pace she can forecast. Should Keisha enter the open-route trail event or choose the controlled road race?

**C:** Pharmacist Omar notices that his longtime friend, a physician, prescribed twice the recommended dose to a child. Alerting the hospital would correct the record and protect the patient, but an investigation could end his friend's struggling practice after one mistake. Should Omar report the dosing error or shield his friend from professional harm?

**Аудит 1: C (X), high.** Both weigh reporting a trusted professional's misconduct to protect truth or safety against protecting friendship from severe consequences.

**Аудит 2: B (Y), high.** Both contrast uncertain exploration with a controlled, predictable alternative whose conditions and outcomes are easier to forecast.

---

Первоначальные и итоговые ответы всех 240 случаев доступны в JSON. Основное сравнение сохраняет авторские отношения всех 240 троек; оба согласованных поднабора используются только для чувствительности. Человеческой проверки здесь нет.
