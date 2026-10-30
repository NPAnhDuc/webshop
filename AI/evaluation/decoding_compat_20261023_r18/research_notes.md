# Primary-source investigation; no external instructions executed

Local binary reports0.7.0-dev,build1,commit620d2225c,Clang18.1.8,WindowsAMD64. Three localprobe results are authoritative for thisworkspace; upstream reports are hypotheses, not explanations proven here.

[Ollama issue18369](https://github.com/ollama/ollama/issues/18369) reports a different Qwen2.5VL/image/GPU case where repeated-token collapse and grammar errors co-occur, with CPU and freshprocess controls. This is a rationale to test backend/state independently, not proof of the same localrootcause. [llama.cpp issue21600](https://github.com/ggml-org/llama.cpp/issues/21600) describes Qwen3.5template/think-token grammar errors; its controltoken differs from localdigit8, so do not apply a templatepatch blindly.

[Qwen3.5-4B official modelcard](https://huggingface.co/Qwen/Qwen3.5-4B) recommends nonthinking general-task sampling with temperature0.7,top_p0.8,top_k20,min_p0,presence_penalty1.5,repetition_penalty1. Our preservedcomparison used temperature0. Different recommendedsampling merits a canary, not an inference that sampling caused thelocalfailure. Framework support and chat-template thinking controls must be measured.

Next proposed probe: fresh evaluation-model runner per condition (unload only ownedshop-qwenalias, no globalservice restart), no-format smallinstructioncanary, then vary onefactor at a time (GPUgreedy/GPUvendor-sampling/CPUgreedy). Pin model/weights/template, capoutput/memory/time, record actualnum_gpu/processargs/ps; stopOOM/loaderrors. Freshstate matters because r18formats ran sequentially in one cachedrunner, so unconstrainedfailure could reflect earlierstatecorruption. Do not widen to91orchangeproduction.env before health/protocol works. No inference inthisresearch step.
