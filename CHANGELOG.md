# Changelog

<!--next-version-placeholder-->

## v1.0.0 (2022-10-17)
### Feature
* Add matrices and complete Walkthrough.ipynb ([`6aad4ea`](https://github.com/CallumJHays/mathpad/commit/6aad4eabe2bf53fd89c0b7732d1663f006ea8c0e))

### Fix
* **py37:** Import Protocol from typing_extensions ([`b8d0e95`](https://github.com/CallumJHays/mathpad/commit/b8d0e95a96c64adda56a19efdb9309238cd29efb))
* **types:** Undo contravariance for Generic Vec and Val types ([`882c09e`](https://github.com/CallumJHays/mathpad/commit/882c09e1f112fe6b993dd2b45b509476b8759539))
* Make SubstitutionMap keys and vals covariant per pyright's recommendation ([`94ceba3`](https://github.com/CallumJHays/mathpad/commit/94ceba3af36787e0067b70eb8fda6e083a164b83))
* Replace SubstitutionMap with contravariant equivalent and fix examples ([`462f670`](https://github.com/CallumJHays/mathpad/commit/462f670ccf532be6c0b41c190ff4489a371ec501))

### Breaking
* Replace SubstitutionMap with contravariant equivalent and fix examples ([`462f670`](https://github.com/CallumJHays/mathpad/commit/462f670ccf532be6c0b41c190ff4489a371ec501))

### Documentation
* Update walkthrough and readme ([`d6dc4ee`](https://github.com/CallumJHays/mathpad/commit/d6dc4ee9f534797b3978d3b38abf8a7af3b916f1))

## v0.2.3 (2022-10-11)
### Fix
* Get examples working in jupyterlite ([`ce7d164`](https://github.com/CallumJHays/mathpad/commit/ce7d1640b069ff0d91f532679b0fe20a1468082a))
* Don't show warning on plot_static=False ([`2711a13`](https://github.com/CallumJHays/mathpad/commit/2711a139fcff3c529583b8fb03de0caaa4327af0))
* Retain frame ID in vectorspace operations ([`b4108e3`](https://github.com/CallumJHays/mathpad/commit/b4108e36707aa131e28da44120afac87d2daec95))
* Don't use \\tiny latex (doesn't render properly sometimes) ([`2592392`](https://github.com/CallumJHays/mathpad/commit/25923927c9cebf2a3b64c41d398c453d6568956e))

### Documentation
* Add output simulation gifs back into examples ([`19e7eb3`](https://github.com/CallumJHays/mathpad/commit/19e7eb3a7127eeab5ba89ef8bab4552bcbb064d2))

## v0.2.2 (2022-10-10)
### Fix
* Simulate_dynamic_system(display_progress_bar=False) ([`5108af7`](https://github.com/CallumJHays/mathpad/commit/5108af7d9cdae43715d08694b7a31fd35eacec02))

## v0.2.1 (2022-10-06)
### Fix
* Now deleted import ([`cbc6ff9`](https://github.com/CallumJHays/mathpad/commit/cbc6ff9a2ea6a0d153f335d204cd5ee58f64c285))

## v0.2.0 (2022-10-05)
### Feature
* Update poetry deps ([`f48768e`](https://github.com/CallumJHays/mathpad/commit/f48768ef3ca05ca457a62ae1e87ad8349d18b2dc))
* Implement vectors ([`81ec08b`](https://github.com/CallumJHays/mathpad/commit/81ec08bc4e7f73960ad7dec209fd0379cf4ce312))
* Implement vectors ([`49b6d17`](https://github.com/CallumJHays/mathpad/commit/49b6d17073bb81a604946a3ba484fe7b908e3c39))

### Fix
* Cannot import 'Literal' from 'typing' in py3.7 (pt2) ([`a3877d7`](https://github.com/CallumJHays/mathpad/commit/a3877d7cd266894f8c8373be391a318499b24bc2))
* Cannot import 'Literal' from 'typing' in py3.7 ([`8c96b68`](https://github.com/CallumJHays/mathpad/commit/8c96b684a280f0860b5f3f5bc47b5661fb63353a))

### Documentation
* Rewrite double pendulum example using vectors ([`787a6e5`](https://github.com/CallumJHays/mathpad/commit/787a6e57f466cb2b225f60c2cc1a959a8f9b7294))

## v0.1.10 (2021-10-24)
### Fix
* Re-add kaleido as a dependency ([`c3cb26d`](https://github.com/CallumJHays/mathpad/commit/c3cb26d3af320fdc2ac27569815424b455c74edb))

## v0.1.9 (2021-10-24)
### Fix
* Patch to avoid bug ([`e11579b`](https://github.com/CallumJHays/mathpad/commit/e11579bf0e48de8f09d068d7154480aca98f3fa9))

## v0.1.8 (2021-10-24)
### Fix
* Commit dist directory for python-semtantic-release ([`2f1b2ed`](https://github.com/CallumJHays/mathpad/commit/2f1b2ed85580182f4d9f91f226f737e5b1a8214b))

## v0.1.7 (2021-10-24)
### Fix
* Move kaleido to dev-dependency ([`14f759e`](https://github.com/CallumJHays/mathpad/commit/14f759e017e535007b1089cf78432fa9b63acc0a))

## v0.1.6 (2021-10-24)
### Fix
* Simulate_dynamic_system bug ([`1c9bb3e`](https://github.com/CallumJHays/mathpad/commit/1c9bb3e132001e0cac7640f1e5d4cdd124ee962e))
* Trigger release ([`0f0654d`](https://github.com/CallumJHays/mathpad/commit/0f0654da2d858372491e97c77809fa1a624757c5))

## v0.1.5 (2021-10-23)
### Fix
* Actually plot more illuminating values ([`413fea5`](https://github.com/CallumJHays/mathpad/commit/413fea5185345bb4481b2095a397be8a0ced11cd))
* Plot more illuminating values ([`987bbd4`](https://github.com/CallumJHays/mathpad/commit/987bbd4d80cae10960b98c7348168f5b3c2c79cd))
* Simulate_dynamic_system integration step order ([`6d666df`](https://github.com/CallumJHays/mathpad/commit/6d666df504e1a6e6a5313f78a3502777f5f1c850))

## v0.1.4 (2021-10-22)
### Fix
* Make example plots non-interactive so they display on github ([`9fd9a76`](https://github.com/CallumJHays/mathpad/commit/9fd9a760b37323efb167fdbd80b6285e552d266f))

## v0.1.3 (2021-10-22)
### Fix
* Remove @equation ([`d140be5`](https://github.com/CallumJHays/mathpad/commit/d140be505b8f878fad9e07bcba76585991c13328))

## v0.1.2 (2021-08-29)
### Fix
* Version ([`9d30de8`](https://github.com/CallumJHays/mathpad/commit/9d30de8b293d1cc908ad96f542e76825a7d75a17))

## v0.1.0 (2021-08-16)

-   Initial version
