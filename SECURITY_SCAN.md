_Last updated: 2025-10-11 04:18:36 UTC_


## pip-audit



## bandit

Working... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
Run started:2025-10-11 04:19:06.327969

Test results:
>> Issue: [B110:try_except_pass] Try, Except, Pass detected.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b110_try_except_pass.html
   Location: /hidden/app/routers/document_upload.py:255:20
254	                            await file_manager.delete(temporary_path)
255	                    except Exception:
256	                        pass
257	

--------------------------------------------------
>> Issue: [B110:try_except_pass] Try, Except, Pass detected.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b110_try_except_pass.html
   Location: /hidden/app/routers/document_upload.py:261:24
260	                            await file_manager.delete(revision_path)
261	                        except Exception:
262	                            pass
263	

--------------------------------------------------
>> Issue: [B110:try_except_pass] Try, Except, Pass detected.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b110_try_except_pass.html
   Location: /hidden/app/routers/document_upload.py:274:12
273	                lru.delete(thumbnail_path)
274	            except Exception:
275	                pass
276	

--------------------------------------------------

Code scanned:
	Total lines of code: 5703
	Total lines skipped (#nosec): 0
	Total potential issues skipped due to specifically being disabled (e.g., #nosec BXXX): 8

Run metrics:
	Total issues (by severity):
		Undefined: 0
		Low: 3
		Medium: 0
		High: 0
	Total issues (by confidence):
		Undefined: 0
		Low: 0
		Medium: 0
		High: 3
Files skipped (0):
