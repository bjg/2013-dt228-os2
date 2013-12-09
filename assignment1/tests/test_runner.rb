#!/usr/bin/env ruby

require 'fileutils'

class Specs
  def initialize(shell)
    @shell = shell
  end

  def run(cmd)
    result = %x{echo '#{cmd}' | #{@shell} 2>/dev/null}.split(PROMPT)
    return result[1].chomp if result.length >= 2
    "" 
  end

  def single
    %x{uname}.chomp == run(path_for('uname'))
  end

  def with_args
    %x{expr 1 + 1}.chomp == run(path_for('expr') + ' 1 + 1')
  end

  def path_exists
    %x{uname}.chomp == run('uname')
  end

  def path_not_exists
    run('xyz') == ""
  end

  def relative_path
    %x{uname}.chomp == run(relative_path_to(path_for('uname')))
  end

  def globbing
    %x{ls .she*py}.chomp == run('ls .she*py')
  end

  def background
    start = Time.now
    run('tests/sleep.sh &\ntouch l.l')
    created = File.ctime('l.l')
    File.delete('l.l')
    created - start < 2
  end

  def redirect_to
    run('echo redirection > outfile.txt')
    begin
      File.open('outfile.txt') do |f|
        return f.gets.chomp == 'redirection'
      end
    rescue
      false
    end
  end

  def redirect_from
    run('cat < outfile.txt') == 'redirection'
  end

  def pipeline
    %x{ls -l | cat | wc -l}.chomp == run('ls -l | cat | wc -l')
  end
end

def msg(*args)
  unless @quiet
    $stderr.print *args
    $stderr.print "\n"
  end
end

def fail(*args)
  unless @quiet
    $stderr.print "\n"
    $stderr.print "Fail: "
  end
  msg *args
  @fails += 1
end

def fail_and_exit(*args)
  @quiet = false
  fail(*args)
  exit 1
end

def current_depth
  ENV['PWD'].split('/').size - 1
end

def relative_path_to(file)
  '../' * current_depth + file
end

def path_for(cmd)
  %x{which "#{cmd}"}.chomp
end


TIMEOUT=2
@passes=0
@fails=0
@run=0
@grade = 0.0
PROMPT=%x(make --silent showprompt 2>/dev/null).chomp
PROMPT="sh>> " if PROMPT == ""
@grading = ARGV.include? "--grade"
@quiet = @grading


@assertions = [
  {tc: 'Run a command with no arguments', cmd: :single, explanation: "Unexpected output from running the a command", marks: 0 },
  {tc: 'Run a command with a multiple arguments', cmd: :with_args, explanation: "No support for passing command line arguments", marks: 0 },
  {tc: 'Check if PATH lookup is implemented for a command that exists', cmd: :path_exists, explanation: "Command in PATH but not executed ", marks: 0 },
  {tc: 'Check how PATH lookup is implemented for a command that does not exist', cmd: :path_not_exists, explanation: "Command not in PATH but expected error not thrown", marks: 0 },
  {tc: 'Check if relative path commands will run', cmd: :relative_path, explanation: "Relative path command not executed ", marks: 0 },
  {tc: 'List files using a glob', cmd: :globbing, explanation: "Expected to be able to list files with globbing", marks: 5 },
  {tc: 'Check if command backgrounding is implemented', cmd: :background, explanation: "Command backgrounding not implemented or not working", marks: 5 },
  {tc: 'Check if output redirection is implemented', cmd: :redirect_to, explanation: "Output redirection not implemented or not working", marks: 5 },
  {tc: 'Check if input redirection is implemented', cmd: :redirect_from, explanation: "Input redirection not implemented or not working", marks: 5 },
  #{tc: 'Check if command pipelining is implemented (no command arguments)', depends: :EXTERNAL, cmd: 'uname | wc' , expected: %x{uname | wc}.chomp, explanation: "Command pipelining not implemented or not working", marks: 2.5 },
  {tc: 'Check if command pipelining is implemented (with command arguments)', cmd: :pipeline, explanation: "Command pipelining not implemented or not working with command arguments", marks: 5 },
  #{tc: 'BONUS (Not graded): Check if simultaneuous input and output redirection is implemented', depends: :EXTERNAL, cmd: 'cat < outfile.txt > /dev/tty' , expected: 'redirection', explanation: "Simultaneous use of < and > not implemented or not working", marks: 0 },
  #{tc: 'BONUS (Not graded): Check if multi-stage pipelining is implemented', depends: :EXTERNAL, cmd: 'uname -a | cat | wc -l' , expected: %{uname -a | cat | wc -l}.chomp, explanation: "3-stage pipeline not implemented or not working", marks: 0 },
  #{tc: 'BONUS (Not graded): Check if internal commands can be pipelined', depends: :EXTERNAL, cmd: 'env|grep PATH' , expected: '/usr/bin', explanation: "3-stage pipeline not implemented or not working", marks: 0 },
  #{tc: 'BONUS (Not graded): Check if all redirection features work together', depends: :EXTERNAL, cmd: 'cat < outfile.txt | cat > /dev/tty ' , expected: 'redirection', explanation: "Multifuncitonal redirection not implemented or not working", marks: 0 },
]

specs = Specs.new(ARGV[0])
begin
  @assertions.each_with_index do |test, i|
    msg "unit-test-#{i}: " + test[:tc]
    @run = i + 1
    if specs.send(test[:cmd])
      @passes += 1
    else
      fail test[:tc]
    end
  end
rescue => e
  fail_and_exit e
end

msg "\n#{@passes} out of #{@assertions.size} tests passed of #{@run} test cases run. "
if @run < @assertions.size
  msg "#{@assertions.size - @run} test cases could not run. Fix failing unit-test-#{@run - 1} to proceed"
end
if @grading
  $stderr.print "#{@grade}\n"
end

exit 0
