# POC Testing for PowerPoint Generation Service

Simple testing to validate the core POC functionality works.

## What We Test

✅ **Core Functionality**: Document input → PowerPoint output  
✅ **Document Tag**: `[document]` tag works (single supported format)
✅ **Empty User Message**: Works with just document content
✅ **User Instructions**: Can add instructions before document

**Note**: Only `[document]` tag is supported for consistent high quality. Legacy tags removed.  

## Running the Test

```bash
# Make sure service is running first
func start --port 7072

# Run the POC validation
python test_poc.py
```

## Expected Output

```
==================================================
POWERPOINT GENERATION POC TEST
==================================================
Service is available, running tests...

Core Functionality (Document Tag):
Testing new [document] tag...
  SUCCESS: 19.2s, 50KB, presentation_PPT2307202512E7CA41.pptx

Empty User Message:
Testing empty user message...
  SUCCESS: 18.7s, 48KB, presentation_PPT2307202580554462.pptx

User Instructions:
Testing with user instruction...
  SUCCESS: 20.7s, 51KB, presentation_PPT23072025575C4766.pptx

==================================================
POC TEST RESULTS
==================================================
Core Functionality (Document Tag): PASS
Empty User Message: PASS  
User Instructions: PASS

Overall: 3/3 tests passed

POC VALIDATION: SUCCESS
The PowerPoint generation service is working correctly!
```

## What This Validates

- ✅ Service responds to HTTP requests
- ✅ Document parsing works (both new and legacy formats)
- ✅ AI pipeline processes content correctly  
- ✅ PowerPoint files are generated successfully
- ✅ Files are saved locally and returned as base64
- ✅ Processing times are reasonable (~15-20 seconds)
- ✅ File sizes are appropriate (~50KB)

That's all you need to validate your POC works! 🎉