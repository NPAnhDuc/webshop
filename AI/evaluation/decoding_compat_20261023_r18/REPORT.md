# Decoder compatibility r18: removing schema is not a usable workaround

Three preregistered requests use identical firstfailedr17messages/options/localalias; only format differs. No semanticgold sent/scored, no productioncode/model/configchange. All3attempted/integritytrue, no runner remains. AllHTTPbodies,newruntimeerrors and rawsuccessfulresponse reviewed.

|Mode|HTTP|Result|
|---|---:|---|
|Fullschema|500|Grammarstackexception on digit8|
|JSONobject|500|Sameexception|
|Noformat|200|300digits8, lengthstop, not required JSONobject|

No valid output contract (0/3). StrictJSON parsing of repeateddigits yields a number, then contractcheck rejects; HTTP200 or JSONsyntax alone is not success. Do not ingest thisoutput, score modelquality, or disableformat inproduction. Twoerrorresponses now preserved with theiractualbody and matchednewruntimeerrorlines. No observedOOM/loadfailure. Actualqwen35aliasctx6144loaded; localbinary0.7.0-dev,build1,commit620d2225c. Total30.548s includes25.25sfirstcallload, not usablethroughput/qualityscore.

Cause remains unproven. All3modes shared one cachedrunner, so earlierfailures may have affected laterstate; cannot conclude independentno-formatdecoding is intrinsically broken. Primary-source analogues suggest testing freshstate/backend/sampling separately, but they involve differentconditions; see research_notes.md for linkedofficialrepoissues andmodelcard, notclaimedfixes. Qwenmodelcardrecommendednonthinkingsampling differs from preservedtemp0test; no settingschangedthisheartbeat.

Next boundedprobe should use a smallno-formatinstructioncanary, freshly unload/reload only evaluationalias percondition, compareGPUgreedy/GPUdocumentedsampling/CPUgreedy onefactoratatime withactualoffloadverified. Freezeconditionsbeforecalls, capmemory/output/time, stoponOOM/loaderror, no globalservice/runtimeupgrade orproduction.envchange. Healthcanary is not full91qualitycomparison; afterhealthybackend, schema/protocol stillneedsvalidation. Originalr17staysstopped. No extra batchthisheartbeat, no reserved/validation/paidAPI/Colab/finetune/deploy/subagents/messages. Activepatch9hashesunchanged; lastaccepted450/479development,87/100legacy,193testslastpassed.
