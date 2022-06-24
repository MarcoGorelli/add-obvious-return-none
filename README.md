Tool and pre-commit hook to add obvious `-> None` to Python files.

WIP

Usage:

```diff
$ python add_obvious_return_types.py my_file.py 
$ git diff -- my_file.py
diff --git a/my_file.py b/my_file.py
index 536cdc7..c52e786 100644
--- a/my_file.py
+++ b/my_file.py
@@ -1,4 +1,4 @@
-def foo(a: bool):
+def foo(a: bool) -> None:
     if a:
         return
     a += 1
```
