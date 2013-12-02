MYSH=.shell.py

default: $(MYSH)

PROMPT = "sh>> "

.PHONY: clean showprompt listfeatures

.shell.py: shell.py 
	@echo "#!/usr/bin/env python3" > $@
	cat $< >> $@
	@chmod +x $@

tests: .shell.py tests/test_runner.rb
	@tests/test_runner.rb $(shell pwd)/.shell.py && rm .shell.py

grade: .shell.py tests/test_runner.rb
	@tests/test_runner.rb $(shell pwd)/.shell.py --grade && rm .shell.py

clean:
	rm -f *~ tests/*~ .shell.py shell.log

listfeatures:
	@echo EXTERNAL

showprompt:
	@echo $(PROMPT)
