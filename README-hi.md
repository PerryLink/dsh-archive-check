# dsh-archive-check — अभिलेख पंजीकरण की पूर्णता और अवधारण अवधि की जाँच

`dsh-archive-check` एक 归档登记表 (फाइलिंग रजिस्टर) पढ़ता है — रजिस्टर में जो कॉलम हैं उनके साथ प्रत्येक प्रविष्टि, तथा वह जिस फंड और वर्ष को समेटता है — और वह जाँचता है जो एक रजिस्टर से यंत्रवत् अपेक्षित किया जा सकता है: क्या प्रत्येक प्रविष्टि में आपके द्वारा कॉन्फ़िगर किए गए विवरण-कॉलम भरे हैं, क्या 档号 रजिस्टर के भीतर अद्वितीय है, क्या 件号 बिना अंतराल के चलता है, क्या 保管期限 आपकी ही अवधि-सूची का कोई शब्द है, क्या 形成日期 पढ़ी जा सकती है और रजिस्टर के वर्ष से मेल खाती है, और क्या आपके कॉन्फ़िगर किए गए हस्तांतरण-काल की अवधि पूरी कर चुकी प्रविष्टियाँ दर्ज होती हैं।

## यह किन सवालों का जवाब देता है

| आपका सवाल | इसका जवाब |
|---|---|
| मैंने कोई अनिवार्य विवरण-कॉलम कॉन्फ़िगर नहीं किया। क्या विवरण की जाँच चुपचाप पास हो जाती है? | नहीं। जब तक `requiredFields` खाली है, `AR-001` स्वयं को `skipped` में दर्ज करता है, इसलिए खाली अंतर-सूची को «कुछ कम नहीं है» नहीं पढ़ा जाता। अपने कॉलम-नाम भरने के बाद यह केवल यह देखता है कि हर प्रविष्टि में वे कॉलम भरे हैं (खाली स्ट्रिंग अपूर्ण मानी जाती है); विवरण सही है या नहीं, यह नहीं आँकता। |
| दो प्रविष्टियों का 档号 एक ही है, पर एक में बीच में खाली जगह है। क्या यह फिर भी दोहराव है? | हाँ। `AR-002` 档号 की तुलना करते समय खाली जगह नज़रअंदाज़ करता है, इसलिए 「A-2026-001」 और 「A-2026- 001」 एक ही क्रमांक माने जाते हैं। यह `warn` तक सीमित है क्योंकि जिस धारा का यह हवाला देता है वह अद्वितीयता को संकलन-सिद्धांत कहती है, एक ही रजिस्टर में दोहराव पर शब्दशः रोक नहीं; कोई हिट आम तौर पर दोहरा पंजीकरण या गलत 档号 बताता है, जिसकी पुष्टि व्यक्ति को ही करनी होती है। |
| 保管期限 कॉलम में ऐसा कुछ लिखा है जो हमारी अवधि-सूची में नहीं है। जाँच क्या बताती है? | `AR-003` दो स्थितियाँ अलग रखता है: ऐसा मान जिसे पार्सर अवधि-शब्द के रूप में पहचान ही नहीं पाता (पहचाने जाने वाले शब्द हैं 「永久」「长期」「定期N年」「N年」), और ऐसा पहचाना गया शब्द जो आपकी कॉन्फ़िगर की गई `retentionTerms` सूची में नहीं है। सुधार अलग-अलग हैं, इसलिए संदेश भी अलग-अलग हैं। यह नियम कभी तय नहीं करता कि किस दस्तावेज़ के लिए कौन-सी अवधि उचित है, और राष्ट्रीय ढाँचे से लंबी अवधि त्रुटि नहीं है: पैक जिन प्रावधानों का हवाला देता है वे उद्यमों के आँकड़ों को न्यूनतम कहते हैं। |
| 件号 1, 2, 4 हैं — छूटा हुआ 3 दर्ज होता है? | हाँ, पर केवल शुद्ध अंकों वाले 件号 के लिए: `AR-004` क्रम-निरंतरता केवल उन्हीं की जाँच करता है; अक्षर या खाली जगह वाले 件号 तुलना में नहीं आते और कोई अंतर भी दर्ज नहीं होता। अंतराल अपने आप में दोष नहीं — हो सकता है वह क्रमांक इस्तेमाल ही न हुआ हो — इसलिए हिट केवल यह जाँचने को कहता है कि कोई प्रविष्टि पंजीकृत रह गई है या नहीं। `checkSequence: false` पर यह नियम चलता ही नहीं। |
| 形成日期 「二〇二六年三月十五日」 लिखी है। क्या यह पढ़ी जाएगी? | नहीं। `AR-005` इसे «पढ़ा नहीं जा सका» बताता है, जो उस तिथि से अलग संदेश है जिसका वर्ष रजिस्टर के वर्ष से मेल नहीं खाता — दोनों के सुधार अलग-अलग हैं। वर्ष-पार संग्रहण की अनुमति है, और यह नियम तय नहीं करता कि कोई दस्तावेज़ किस वर्ष में रखा जाना चाहिए। |
| जाँच को कैसे पता चलता है कि हस्तांतरण की अवधि आ गई? | `AR-007` प्रत्येक प्रविष्टि की 形成日期 की तुलना आपके कॉन्फ़िगर किए `transferAfterYears` से करता है और केवल यह दर्ज करता है कि निर्धारित वर्षों के अनुसार वह अवधि बीत गई या नहीं। यह पैरामीटर फ़ैक्टरी में `0` है, यानी कॉन्फ़िगर नहीं किया गया, इसलिए जब तक आप इसे सेट न करें यह नियम स्वयं को `skipped` में दर्ज करता है; `requireFormedAt: true` करने पर बिना 形成日期 वाली प्रविष्टियाँ भी अलग से दर्ज होती हैं, क्योंकि बिना तिथि के देय-तिथि निकाली नहीं जा सकती। यह नियम यह नहीं आँकता कि हस्तांतरण आगे बढ़ाया जाए या टाला जाए। |

## यह किन मानकों पर आधारित है

| दस्तावेज़ | संख्यांक | इन्हें उद्धृत करने वाले नियम |
|---|---|---|
| 《归档文件整理规则》 | DA/T 22—2015 | AR-001, AR-002, AR-004, AR-005, AR-006 |
| 《中华人民共和国档案法实施条例》 | 国务院令第772号 | AR-001, AR-003, AR-007 |
| 《机关文件材料归档范围和文书档案保管期限规定》 | 国家档案局令第8号 | AR-003 |
| 《企业文件材料归档范围和档案保管期限规定》 | 国家档案局令第10号 | AR-003 |
| 《中华人民共和国档案法》 | 2020年修订（主席令第四十七号） | AR-007 |

**Boundary:** this plugin checks one **归档登记表** (filing register) for the things a register can be
held to mechanically — that each item is described completely enough to be filed and found again, that
档号 is unique, that 件号 runs without gaps, that retention terms come from your schedule, and that
形成日期 parses and matches the register's year. It does **not** decide whether a particular document
belonged in the archive, nor which retention period it deserves. Those are the archivist's judgements.

> ### ⚠️ Three things this plugin refuses to do, and why
>
> **1. It never decides which retention period a document deserves.** There is **no single national
> retention table** you can apply. 《档案法实施条例》第十九条第二款 and 国家档案局令第8号第十二条 require each
> institution to compile its own 归档范围 and 保管期限表 and have it approved by the档案 authority; and
> 国家档案局令第10号第十一条 says the enterprise figures are a **minimum** — an enterprise may lawfully
> choose a *longer* period. So `AR-003` checks only that the wording is one you have configured, and a
> test asserts that the pack says a longer period "is not an error".
>
> **2. It puts the transfer years where they belong.** The 20-year / 10-year figures are in
> **《档案法实施条例》第二十条第二款**, keyed to the *receiving archive's level*, not to whether the unit
> is an enterprise. 《档案法》第十五条 contains **no year figure at all** — it says only "按照国家有关规定，
> 定期". Attributing "满20年" to the law's article 15 would be fabrication, and a test asserts the pack
> does not.
>
> **3. It does not use the outdated first article.** 国家档案局令第8号's 第一条 cites the 1999
> 《档案法实施办法》, which the 2024 条例 (国务院令第772号) repealed in its 第五十二条. The pack never cites it,
> and a test asserts that.
>
> Two lists are yours, not the law's: the required description fields (`AR-001`) and your retention
> vocabulary (`AR-003`). Both ship **empty**, and a rule whose list is unset reports itself in `skipped`
> rather than passing silently.

## Compatibility

| सतह | स्थिति |
|---|---|
| Harness | peer रेंज `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — `0.2.0-rc.2` और `0.2.1-alpha.1` दोनों को स्वीकार करने के लिए सत्यापित। **`engines.dsh` जानबूझकर घोषित नहीं**: इसका कोई पाठक नहीं और यह किसी होस्ट को अस्वीकार नहीं कर सकता |
| Node | `^22.19.0 || >=24.0.0` |
| प्लेटफ़ॉर्म | सभी (शुद्ध ESM; कोई नेटिव कोड नहीं, कोई नेटवर्क नहीं, कोई मॉडल कॉल नहीं) |
| टूल मोड | `native`, `ptc` और `both` में काम करता है; पूरे फ़ोल्डर के लिए `ptc` चुनें |

## What it does

नियम-सूची, फ़ील्ड और विस्तृत व्यवहार [README.md](README.md#what-it-does) (अंग्रेज़ी मुख्य संस्करण) में हैं। यह प्लगइन केवल उद्धृत धाराओं के सामने शाब्दिक अंतर सूचीबद्ध करता है और हर न चल पाई जाँच को `skipped` में बताता है।

## Install

```sh
dsh plugin --profile <name> add dsh-archive-check
dsh --profile <name> --dump-config | grep 'dsh-archive-check'
```

## Configuration

सभी समायोज्य पैरामीटर `src/config.ts` की Schemastery स्कीमा में हैं, इसलिए कोड बदले बिना `cordis.yml` से बदले जा सकते हैं; प्रति-नियम सीमाएँ `rules/` के नियम-पैक में हैं।

| कुंजी | प्रकार | डिफ़ॉल्ट | विवरण |
|---|---|---|---|
| `rulesFile` | string | `rules/archive-check.yaml` | नियम-पैक का पथ, पैकेज रूट के सापेक्ष |
| `disabledRules` | string[] | `[]` | बंद करने वाले नियम id; प्रत्येक `skipped` में दिखता है |
| `onlyRules` | string[] | `[]` | केवल ये नियम चलाएँ; खाली होने पर सभी नियम चलते हैं |
| `skipNotes` | string | `""` | हर `skipped` कारण के आगे जोड़ी जाने वाली टिप्पणी |
| `timeoutMs` | number | `120000` | उपकरण का सहकारी समय-सीमा बजट |

## Material format

JSON या YAML स्वीकार्य है। पूरा फ़ील्ड उदाहरण [README.md](README.md#material-format) (अंग्रेज़ी मुख्य संस्करण) में है। पढ़ने की परत में फ़ील्ड वैकल्पिक हैं और जाँच इंजन उन्हें सत्यापित करता है, इसलिए आंशिक निर्यात पर क्रैश के बजाय "अनुपस्थित" श्रेणी के निष्कर्ष मिलते हैं।

## Rule sources

नियम-डेटा कोड से अलग है: प्रत्येक नियम में दस्तावेज़, संख्या, स्रोत की अपनी क्रमांकन-प्रणाली के अनुसार धारा, शब्दशः उद्धरण और स्रोत URL होता है। लोडर लागू करता है कि उद्धरण कम से कम आठ अक्षरों का वास्तविक उद्धरण हो, और जिस जाँच का आधार केवल सामान्य सिद्धांत (`kind: derived-from-principle`, अधिकतम `warn`) या स्थानीय नीति (`kind: institutional-configuration`, अधिकतम `info`) हो, उसे कभी `error` घोषित न किया जाए।

सत्यापित सीमाएँ और जान-बूझकर **न** कहे गए निष्कर्ष [README.md](README.md#rule-sources) (अंग्रेज़ी मुख्य संस्करण) और `rules/evidence/` में हैं।

## Troubleshooting

- **प्लगइन इंस्टॉल हो गया पर टूल दिखता नहीं**: जाँचें कि `main` `lib/index.mjs` पर जाता है और `pnpm run build` ने उसे बनाया है।
- **`dsh plugin add` असंगत बताकर मना करता है**: peer range `0.1.x` और `0.2.x` दोनों को कवर करती है; बाहर होने पर स्पष्ट छूट दें: `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`।
- **कोई नियम नहीं चला**: `skipped` सरणी देखें।
- **`check` में `manifest-peers` विफल दिखता है**: यह `dsh-plugin-dev` की ज्ञात अपस्ट्रीम समस्या है; रनटाइम इंस्टॉल के समय अनुकूलता लागू करता है।
- **समय खिसका हुआ लगता है**: सारी गणना दिए गए स्ट्रिंग पर वॉल-क्लॉक है।

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-archive-check
```

अंतिम कमांड `../_shared` का साझा किट `src/shared/` में कॉपी करता है; हर साझा बदलाव के बाद इसे दोबारा चलाएँ।

## License

[Apache License 2.0](LICENSE) © 2026 dsh-archive-check contributors.
