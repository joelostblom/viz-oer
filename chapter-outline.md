# Chapter outline

1. Chapter summary (Learning objectives + their solutions in a sentence)
    - E.g. instead of stating a LO like "Apply faceting operations to charts",
      we would say "Apply the `facet` method to group data into multiple subset
      based on the unique values of a variables. This is helpful when we want to
      compare subsets of data in a more explicit manner than by e.g.
      coloring the points according to their value/group."
    - I wonder if it would be convenient if these were somehow linked to the sections in the chapter
      that describe each LO in more detail.
      It seems like it could easily become redundant with the ToC,
      but a reminder to students when they read each section
      that they have just "completed" a LO would maybe be helpful
      both to feel that they are making progress
      and to remind them about what was important in the section they just read?
          - Maybe a note or even a progress indicator in the margin?
            "Learning objective N completed" / "Chapter 20% complete" / "You just learned that..."
            There could also be exercises after each LO, more on that later.
2. Required readings? It's somewhat odd to have this in a textbook
   the same way I now have it in the lecture notes.
   But I would like to somehow
   guide the learner toward additional resources
   that the can use to complement what we are teaching,
   e.g. a more in depth chapter/section in "Fundamentals of data visualization".
3. An activity that forces/encourages them to activate and participate right away.
   (this could also be #1, but not sure if it will be disjoint to then have the LOs before getting to the text)
    - I think this is ideally something like a problematic chart or statement
      illustrating how what students have learned up until this point
      is not sufficient to solve the problem we are demonstrating,
      so that they appreciate the need and importance to learn more.
        - Maybe this could be the students studying a viz
          to define the problem with applying only what we have learned so far
          to solve the scenario we set up
          (ideally a scenario with direct practical implications).
          In general, I believe that learning to think about about what the problem is
          given a certain (business) question is beneficial
          instead of that we spoon-feed them the problem statement
          and let them only think about the solution.
          I like the idea of making them come up with as much as possible themselves,
          then they are motivating why the chapter is important on their own
          and there is less "convincing" needed.
            - E.g.
                > In the previous chapter we learned about
                  visualizing each row in a dataframe using a point mark
                  and best practices when mapping data to graphical objects/elements.
                  In the following chart we have followed these best practices
                  when plotting ...{insert some scenario},
                  but it is not easy to extract the main takehome message
                  (or any info for that matter).
                  How can this be given that we followed everything we know so far?
                  Study the chart and think for yourself what has gone awry here
                  and write down a suggestion for what you would do to fix it.
                  {maybe provide a space in the book where they can write,
                  it's ok that it is not saved,
                  it just for them to formally put their thoughts into words
                  which makes it easier to remember}.
                  {show chart}
4. An interesting question for some domain that is relevant to the students
   and/or that we think are an important problem in the world.
   This could be really interesting and real-world anchored,
   such as public health data,
   or a made-up narrative with a real data set
   (such as lab 4 when we look are real language data,
   but from the eyes of an alien).
    - Ideally, there would be some continuity between chapters in this narrative,
      but I'm hesitant to make that a requirement at this point,
      as I also want us to be able to use data from different domains.
      The only way I see us connecting such widely different data
      is through a narrative like that in labs 1-3,
      where we go a bit quirky and very "out there",
      which could be quite appreciated,
      but I would also be OK with having a less humorous narrative 
      and the connection is only how the visualization principles tie into each other
      but the data is more independent for each chapter.
5. A theory section on LO 1.
6. A coding section on LO 1.
    - Should this be a separate section
      so that the book is modular and easy to extend with any charting library?
      Or interwoven with the theory so that there is a more direct connection?
    - Maybe if we have short section and atomic LOs,
      we can get the best of both worlds?
      - What about LOs that are about coding / theory only?
7. A few (~2?) exercises related to LO 1.
    - A mix of theory and coding,
      focus on conceptual understanding of both
      rather than memorization.
    - Should be encompassing.
      I want to be able to tell students that
      if they go through all the exercises in the book (and the labs),
      then they are well-prepared for the quiz
      (without me having to give out any worksheets
      and maybe even without having to give out a practice quiz,
      but that's less important).
    - For theory,
      we could use different question types.
      An easy one to implement would be multiple choice,
      but I also want student to think of some more open ended questions
      at least for the end of the chapter.
        - I like open ended questions
          because they force students to identify the key question problem
          and generate the space of possible solution
          rather than just selecting a solution from a pre-specified list of possibilities
          (this is more real-life like too).
    - Given that we want to focus on conceptual understanding,
      and include both open ended essay question
      and coding questions,
      I think it will be the easiest to not try to implement any type of autograding.
      Although autograding is practical,
      I'm more and more leaning towards that it takes away from the conceptual
      and open ended elements of learning,
      since it tends to required rather structured question design
        - At least this seem to be true for single visualization specifications,
          for more general programs it is easier to envision some test cases
          that still give the student full freedom in how to implement the program
          as long as the tests pass.
          Maybe we can be creative and come up with something similar,
          but it will be lower priority.
        - Instead, we will have hints and solutions.
          To encourage students to think for themselves
          we could have a single button that generates hints on the first 1-2 clicks
          and then shows the full solution in the next click.
          I think this will make it a bit less tempting to just glance at the solution
          instead of doing the exercise
          and seeing part of the solution in the hint
          might spark an idea before they click through the full solution
          (a potential danger is that it is annoying for someone
          who is quickly skimming solutions to review for a quiz,
          so we will have to think about if that's an important use case
          that we want to encourage/enable).
        - One positive aspect of autograding that is harder to emulate
          is that it gives some degree of personalized feedback to the student
          based on the code they have so far.
          A more "out there" idea in terms of achieving this without autograding,
          could be one of the following:
            - A peer feedback system where students get extra credit
              for reviewing their peers code/answers in the textbook.
              This would be difficult to track,
              but could maybe create an additional social aspect
              and it enables peer learning also for the reviewer.
              However,
              given the time available for MDS students,
              this approach is likely unrealistic
              and it would also not be helpful for students outside MDS
              who want to go through the book.
            - AI feedback where we provide an LLM
              with both the student solution and the correct solution
              and asks it to compare the two
              and then help guide the student on the right path
              similar to how an educator would do it
              rather than giving the answer directly.
              The LLM could ingest the content of the book,
              with a higher fine-tuning weight on the current chapter/section maybe
              (if a general one is not good enough)?
              If this works well,
              it would be fantastic
              and students would essentially have access to a tutor right there in the textbook.
              Both special made (Chat)GPTs and Khanmigo (an education bot from Khanacedmy)
              could be promising candidates.
              - I'm quite interested in this direction as it is a lower stakes environment
                than labs/quizzes where students receive marks
                and we could get useful feedback from students on how well it works.
8. Repeat 5-7 until we have gone through all LOs for that chapter.
    - Aim to keep chapters short overall.
      There does not need to be exactly one chapter per lecture in MDS,
      it could be 2-3
      (it's convenient if it is a whole number though).
9. A few exercises that mix LOs together
   so that students practice interleaving concepts
   and that also act as a summary of the chapter?
    - Do we still need a more explicit written summary as a separate section?
      We could also ask students to reflect on what they learned in the chapter themselves
      and write down a summary (this is also in line with effective pedagogies such as
    - I also like what we discussed a couple of calls ago
      around synthesizing a graphical summary of how the key rules in the chapter
      ties into each other.
      Maybe we could even ask student to draw this and then show our drawing.
      I have read that retrieval practice is a more effective learning strategy
      than drawing concepts maps,
      but this would still ask them to do some retrieval as part of the drawing,
      and there are plenty of retrieval exercises throughout the rest of the chapter.
        - Again here it would be really cool to collect what students draw
          and get ideas for how to improve the content.
          - In general I think student do so much work and have so many ideas
            that we are not yet good at leveraging as educators.
            This is why I started the extra credit assignment in 531,
            but more could be done I think
            (although an easy solution would be to ask student to submit
            what they drew as part of the extra credit
            for a chapter where they thought the solution was missing something
            that they had included).
10. A challenging section where students who are interested and capable of going deeper
    gets a chance to do so.
    I open to that this section does not use the same data as the rest of the chapter.
    That would allow us to include well known visualizations here,
    and discuss some historical anecdotes
    together with an advanced theoretical and/or coding section.
    These sections can be brief and include just one (or even no?) exercise.
    It's really to show interested students more depth
    and pique their curiosity and "aw"-factor further.
      - I have been pushing for that we should include these sections
        in our courses in general in MDS,
        so this would be a great opportunity to try out the concept.

## Thoughts and questions

- We want chapters to have a familiar structure to students
  so that they know what to expect as they progress in the book,
  but we don't want them to get bored.
    - One thing I wonder is if there is value in that the chapter design evolves over time
      akin to how levels in video games don't follow quite the same pattern
      even if there are some similar elements like boss fights etc.
      Is there value in introducing this novelty to make students stay engaged?
      I think learning apps like Duolingo also have slightly different level design
      although not as extensive as in a good video game.
        - I'm curious about this,
          but it is an "out there" idea I would say
          and we would be on uncharted waters
          if we start to evolve the book structure
          as the story progresses.
          I think it sounds fun,
          and someone must have written something about this idea in the past
          so maybe we can find a few academic articles to learn more
          if it is considered an effective learning strategy.
            - Maybe we can spend a little time looking at the idea,
              but I don't want this to be a time sink up front
              (although the more I think about it the more it enthralls me =p).
- As part of the grant proposal I wrote about creating videos to enhance students learning.
    - I don't think we are strictly bound by this,
      but if we can think of ways where this complements what students can learn from the text
      then I would like to include it
      as I think it can also mix up the content more
      and engage via different modalities.
        - My initial idea for these videos is around me drawing charts and concepts.
          I think the process of drawing
          is something that students cannot get from a static resource,
          since that will just show the output.
          It could shed light on some conceptual aspect
          and allows students to see aspect laid out more visually.
          For example,
          I drew out a schematic for how all git commands are connecting
          when I originally taught 521,
          and it was really helpful for students to get a graphical overview of what is happening.
- Should we enable comments on the entire book? There are technologies such as `hypothes.is`
  that are easily enabled in quarto
  and allows student to highlight sections in the book and take notes.
  They can even opt to make their notes public to other students
  and have discussions in the comments
  (maybe preferential and more direct vs having discussion on slack?),
  but there would be no notifications and we are splitting discussion into two avenues.
  Maybe more a space to exchange reflections on the content?
- Should there be a dedicated section for common pitfalls?
  This seems hard to execute and I would prefer to bring up pitfalls
  as we go through each section in the chapter
  rather than collect them all in a single section.
    - An alternative to simply bringing it up in the text would be to
      have callout boxes so it is easy to identify the pitfalls for each chapters,
      but they are also occurring right after the section they are related to.
        - Maybe this organization into different callout boxes (or similar semantic unit)
          would allow us to have alternative ways of viewing the content.
          E.g., maybe there could be a way to collate all callout boxes into a single page
          (and like-wise all learning objectives, all excericese, etc separate pages)
          either "on demand" or during the build process of the book.
- Should we have some type of "review what you have learned so far" elements/chapters
  every nth chapter or is that too much hand-holding
  and too much work for us in addition to the existing exercises in each chapter?
  Can it be done in a fun way?
- Should we have a "how to use this book" chapter?
  Or even lay out the philosophy behind some of our choices?
  Maybe at least a short version in some type of foreword,
  but I don't want to students to have to read a manual-like compilation
  before diving in to content.
- Should we store student answers to exercises in a cookie
  so that they are saved when students navigate away from the page?
  If we offered an account and login,
  then they could really track their progress in a more organized way,
  but I'm not sure there is any effective way of doing that
  and now we would have to store it on a server instead.
  We could provide some easy way to download exercises with answer maybe.
  Unsure about this one.  
- Think a bit more about how I will teach in the classroom with this book as a resource.
    - Do I want to teach the same exercises as in the book?
      The advantage is that students can easily review exactly what I taught.
    - Or do I want to teach the same concepts but with slightly different content?
      A bit similar to how my slides now have charts that are not in the lecture notes.
      The advantage is that student 
    - Do I want to make it more of a flipped classroom?
      Not really... I think one of the most interesting and effective parts is how students do peer learning when they use their intuition together for concepts that they are not yet fmailiar with, so it is not just about recalling solutions from the pre-reading, but being creative together.
