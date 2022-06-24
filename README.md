for now, let's ignore:
- functions which have a nested function definition

todo:
	- add test for abstract methods, abstract methods with docstrings
	- if there's a yield, don't rewrite (add test)
	- don't add to init method? check mypy docs
	- figure out how to deal with nested defs?
	- perf
	- don't use regular expressions, use tokenize_rt
	- add test cases for tuple arg defaults, and annotations
	- also infer bool, int, float, str, bytes
	- actually, is that even possible?
	- probably not.
	- rename to `type-obvious-void-returns`
	
