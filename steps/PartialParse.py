class PartialParse:

  def __init__(self, sentence):
    self.sentence = sentence

    self.buffer = list(sentence)

    self.stack = ["ROOT"]

    self.dependencies = []


  def parse_step(self, transition):
    """
    @param transition (str): A string that equals "S", "LA", or "RA" representing the shift,
                                left-arc, and right-arc transitions. You can assume the provided
                                transition is a legal transition.
    """

    if transition == "S":
      """
      SHIFT: removes the first word from the buffer and pushes it onto the stack.
      """
      element = self.buffer.pop(0)
      self.stack.append(element)
    elif transition == "LA":
      """
      LEFT-ARC: marks the second (second most recently added) item on the stack as a dependent of
      the first item and removes the second item from the stack, adding a first word → second word
      dependency to the dependency list.
      """
      second_word = self.stack.pop(-2)
      first_word = self.stack[-1]
      self.dependencies.append((first_word, second_word))

    elif transition == "RA":
      """
      RIGHT-ARC: marks the first (most recently added) item on the stack as a dependent of the second
      item and removes the first item from the stack, adding a second word → first word dependency to
      the dependency list
      """
      first_word = self.stack.pop(-1)
      second_word = self.stack[-1]
      self.dependencies.append((second_word, first_word))

  
  def parse(self, transitions):
        for transition in transitions:
            self.parse_step(transition)
        return self.dependencies



def minibatch_parse(sentences, model):
    def process_partial_parse(partial_parse, count):
      if len(partial_parse.stack) > 1 or count == 0:
          partial_transition = model.predict(partial_parse)
          partial_parse.parse_step(partial_transition)


    """Parses a list of sentences in minibatches using a model.

    @param sentences (list of list of str): A list of sentences to be parsed
                                            (each sentence is a list of words and each word is of type string)
    @param model (ParserModel): The model that makes parsing decisions. It is assumed to have a function
                                model.predict(partial_parses) that takes in a list of PartialParses as input and
                                returns a list of transitions predicted for each parse. That is, after calling
                                    transitions = model.predict(partial_parses)
                                transitions[i] will be the next transition to apply to partial_parses[i].


    @return dependencies (list of dependency lists): A list where each element is the dependencies
                                                    list for a parsed sentence. Ordering should be the
                                                    same as in sentences (i.e., dependencies[i] should
                                                    contain the parse for sentences[i]).
    """
    partial_parses = [PartialParse(sentence) for sentence in sentences]
    unfinished_parses = partial_parses[:]
    dependencies = []
    count = 0
    while True:
      for partial_parse in partial_parses:
          process_partial_parse(partial_parse, count)

      dependencies = [un_parse.dependencies for un_parse in unfinished_parses]


      length_of_stack = [len(un_parse.stack) for un_parse in unfinished_parses]

      if all(length == 1 for length in length_of_stack):
        break

      count += 1

    return dependencies