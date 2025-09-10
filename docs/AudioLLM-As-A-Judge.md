# LLM-as-a-judge for Real-Time Agents

This document outlines the use of LLM-as-a-judge to evaluate and improve the performance of real-time AI agents built using Azure OpenAI or AI Foundry. Compared to other standard agent scenarios where all interactions are text-based, real-time agents often involve multi-modal inputs and outputs, such as voice and images, and require low-latency responses. This document describes a novel approach to adapting the LLM-as-a-judge approach to real-time audio interactions.

## Challenges in Audio-Based Evaluations

Evaluating audio-based interactions is complex and cumbersome due to several factors:

1. **Variability in Speech**: Speech is highly variable, with differences in accents, intonation, and speaking styles. This variability makes it challenging to create a standardized evaluation framework.
2. **Subjectivity**: Evaluating the quality of audio interactions is often highly subjective, as it often depends on individual user preferences and expectations. It may even depend on specific brand guidelines or compliance requirements.
3. **Technical Limitations**: Current evaluation tools and frameworks may not be well-suited for audio-based interactions, necessitating the development of new methods and metrics. Traditional machine learning approaches may be usable but are often not feasible due to high costs and complexity.

Still, there is a need to evaluate audio-based agents as deviations from the instructions can lead to poor user experiences, compliance issues, and brand reputation damage.

## Proposed Approach

To address these challenges, we propose a novel approach that leverages LLM-as-a-judge to evaluate audio-based interactions. For this we are proposing to use the G-Eval framework which relies on the chain-of-thought prompting technique to guide the LLM in evaluating the agent's performance based on any custom predefined criteria. The approach involves the following steps:

1. **Collect Audio Samples**: Gather a set of audio samples from user interactions with the AI agent. For our tests, we only recorded the audio output of the agent to reduce the complexity of the evaluation and also ensure compliance with privacy regulations.

2. **Define Custom Evaluation Criteria**: Define clear and measurable evaluation criteria tailored to the specific audio interaction context. Make sure the evaluation criteria is precise without conflicting objectives. In our tests, we evaluated the dialect of the agent responses.

3. **Chain-of-Thought Prompting**: Develop chain-of-thought prompts that guide the LLM in evaluating the audio samples based on the predefined criteria. The prompt should encourage the LLM to reason through the evaluation process step-by-step.

4. **G-Eval Prompting**: Use the G-Eval framework to combine the evaluation criteria, chain-of-thought prompts and other details highlighted below in a consistent prompt. Also include task instructions and an evaluation form. Ask the agent to provide an explanation for the given score.

```text
# Task Introduction
- You are an assistant that analyzes conversations.
- You will be given a audio input from an agent.
- Your task is to rate the agent's responses based on the evaluation criteria.

# Context
- <context required for the evaluation>

# Evaluation Criteria
- <custom evaluation criteria>

# Evaluation Steps
1. <first step>
2. <second step>
3. <third step>
...
N. <nth step>

# Evaluation Form (scores ONLY):
- <custom evaluation criteria> (1-5): <score> - <brief explanation>

```

5. **Automated Evaluation**: Feed the audio samples and the G-Eval prompts into the LLM to obtain automated evaluations. The LLM will analyze the audio samples and provide scores based on the predefined criteria.

6. **Analyze Results**: Analyze the evaluation results to identify patterns, strengths, and areas for improvement in the AI agent's performance. Use these insights to refine the agent's design and enhance its capabilities.

## Automated Evaluation Workflow

The following steps are part of the automated evaluation workflow:

1. **Define Model endpoint**: Define the model endpoint to be used for the evaluation. We are recommending to rely on the latest `gpt-realtime` model from OpenAI for these evaluations.

2. **Open Real-Time Audio Session**: Establish a real-time audio session with the AI agent to facilitate live interactions and recordings. Provide the G-Eval prompt as an instruction to the agent. Turn off voice activity detection (VAD) to ensure the agent does not start speaking prematurely.

3. **Stream Audio Recording**: Load a collected audio file and stream the audio sample over the real-time session. After streaming the entire audio file, initiate a model response by sending an `input_audio_buffer.commit` event followed by a `response.create` event over the WebSocket.

4. **Process Model Response**: Now the model will respond based on the given instructions. Process the `response.done` event which will contain a transcript of the model response. Process the response to extract the evaluation results.

## Test

In our tests, we asked our LLM-as-a-judge to evaluate how well the provided audio samples adhere to a specific dialect (e.g., British English, American English, Australian English). 

### Generated Audio Samples

Before we started the tests, we generated a few audio samples using a custom application. Throughout the conversation, we recorded the audio output of the agent. 

**Bavarian Audio Sample**
For the first data sample, we instructed the agent to respond with a Bavarian German dialect. This resulted in the following audio sample:

[Bavarian Audio Sample](https://github.com/PerfectThymeTech/real-time-agent/raw/refs/heads/main/docs/audio/bayrisch_strong_accent.wav)

The audio sample shows a strong Bavarian accent which notably is not perfect. Some words are closer to standard German.

**Berlin Audio Sample**
For the second data sample, we instructed the agent to respond with a Berlin German dialect. This resulted in the following audio sample:

[Berlin Audio Sample](https://github.com/PerfectThymeTech/real-time-agent/raw/refs/heads/main/docs/audio/berlinerisch_strong_accent.wav)

The audio sample shows a strong Berlin accent which is notably very distinct from the Bavarian dialect.

### G-Eval Prompt

Let's assume we want our agent to respond in a strong Bavarian dialect. We would use the following G-Eval prompt to evaluate how well the agent adheres to this dialect:

```text
# Task Introduction
- You are an assistant that analyzes conversations.
- You will be given a audio input from an agent.
- Your task is to rate the agent's responses based on the evaluation criteria.

# Context
- Bavarian (Boarisch, Bairisch) is a group of Upper German dialects spoken mainly in Bavaria (southern Germany), Austria, and South Tyrol.
- It differs notably from Standard German in vocabulary, grammar, and pronunciation.
- Typical Bavarian sentences:

| Standard German |	Bavarian |
|-----------------|----------|
| Wie geht es dir? | Wia geht’s da? |
| Mir geht es gut. | Ma geht’s guad. |
| Ich habe Hunger. | I hob an Hunga. |
| Was machst du? | Wos machst? |
| Kommst du mit? | Gheast mid? |
| Es ist sehr kalt. | Es is sakrisch koid. |

- Typical Bavarian words and expressions:
| Standard German |	Bavarian |
|-----------------|----------|
| Ja | Jo |
| Nein | Na / Naah |
| Bitte | Bittschön |
| Danke | Vergelt's Gott |
| Guten Morgen | Guat'n Morgen |
| Gute Nacht | Guate Nacht |
| Auf Wiedersehen | Pfiat di / Pfiat eich |
| Kartoffel | Erdäpfel |
| Junge | Bua |
| Mädchen | Madl / Dirndl |
| sehr gut | sakrisch guad / sauba guad |
| klein | kloi |
| trinken | saufn (colloquial), tringa |
| arbeiten | schaffa |

# Evaluation Criteria
- Accent (1-5) - Rate how well the agent uses a German Bavarian accent. The accent should be consistent throughout the conversation. The accent should not change or vary.

# Evaluation Steps
1. Listen to the audio input carefully and identify the agent's responses.
2. For each agent response, evaluate how well it uses a German Bavarian accent.
3. Assign a score for the Accent on a scale of 1 to 5, where 1 is the lowest and 5 is the highest based on the Evaluation Criteria.
4. Provide a brief english explanation for the rating.
5. Summarize the overall performance of the agent at the end.

# Evaluation Form (scores ONLY):
- Accent (1-5): <score> - <brief explanation>
```

### Results

We now fed the audio samples and the G-Eval prompt into the LLM to obtain automated evaluations according to the process described in [Automated Evaluation Workflow](#automated-evaluation-workflow). The LLM analyzed the audio samples and provided scores based on the predefined criteria.

**Bavarian Audio Sample**

For the Bavarian audio sample, the model assigned the following scores:
```
Accent (1-5): 3 - The agent uses some Bavarian elements, like "Alles klar" and "Um wos für a Gerät geht’s denn," but the overall intonation and pronunciation still lean heavily towards Standard German, lacking the distinct Bavarian melody and vowel shifts. The accent is not fully consistent throughout.

Overall, the agent shows some understanding of Bavarian phrases, but the accent could be more authentic and consistent in tone and pronunciation.
```

Particularly interesting is that the model was able to identify specific Bavarian words and phrases used by the agent without being explicitly told to do so. It also did not rely on the transcript which was generated as it was different from the citations used in the explanation of the model.

**Berlin Audio Sample**

For the Berlin audio sample, the model assigned the following scores:
```
Accent (1-5): 1 - The agent’s accent is not Bavarian at all. It sounds like a Berlin dialect or colloquial German, not the distinctive Bavarian style. There’s no use of Bavarian vocabulary or pronunciation, and the rhythm and intonation do not match Bavarian speech patterns.

Overall, the agent did not demonstrate any Bavarian accent characteristics.
```

Particularly interesting is that the model was able to identify that the sample uses a strong Berlin dialect without being explicitly told what a Berlin dialect is or how it differs from Bavarian.

## Conclusion

The use of LLM-as-a-judge for evaluating audio-based interactions in real-time AI agents shows promise in addressing the challenges associated with variability, subjectivity, and technical limitations. By leveraging chain-of-thought prompting and the G-Eval framework, we can obtain automated evaluations that provide valuable insights into the agent's performance. This approach can be further refined and expanded to cover additional evaluation criteria and scenarios, ultimately leading to improved user experiences and more effective AI agents.

## Next steps

We are considering the following next steps to further enhance the evaluation process:

1. **Expansion of test data**: We plan to expand the test data used for the evaluations to get a better sample population which we can use for benchmarking. Additional data samples will also help to identify edge cases and improve the robustness of the evaluation process.

1. **Classification of accents, dialects, and emotions**: We want to simplify the evaluation setup and want to identify how well the LLM-as-a-judge can classify different accents and dialects, as well as detect emotional cues in speech.

2. **Inclusion of user audio in recordings**: We aim to evaluate how well the agent is able to use the Chain-of-Thought prompting with user audio inputs. We want to understand whether it is able to focus on specific turns in the provided audio sample ignoring user queries.
