## Project Code Quality Standards

I want to build production-ready software that is genuinely usable in the real world. Please follow these standards for all code we write together:

### Core Principles

1. **Simplicity Over Cleverness**
   - Use straightforward solutions, not clever tricks
   - Prefer readable code over "smart" one-liners
   - If it takes more than 10 seconds to understand, it's too complex

2. **Well-Documented**
   - Add comments explaining WHY, not what
   - Document non-obvious decisions
   - Keep README and docs updated as we go
   - Every function should have a clear purpose

3. **Easy to Debug and Maintain**
   - Clear error messages with context
   - Proper error handling (no silent failures)
   - Logging for important operations
   - Meaningful variable and function names

4. **Standard Patterns**
   - Use industry-standard libraries (not obscure ones)
   - Follow language best practices (PEP 8 for Python, etc.)
   - Conventional project structure
   - No experimental or cutting-edge approaches unless necessary

5. **Minimal Dependencies**
   - Only add dependencies we actually need
   - Prefer standard library when possible
   - Document why each dependency exists

6. **Robust and Reliable**
   - Handle edge cases
   - Graceful degradation (fallbacks when things fail)
   - Input validation
   - No assumptions that can break

### Development Process

**Iterative Quality:**
- I understand I'll be exploring features and changing requirements
- This is normal and expected (not "messy prototyping")
- We'll keep code quality high throughout exploration
- We'll refactor continuously, not "later"

**Mutual Responsibility:**
- **You (AI):** Alert me when code is getting complex or messy
- **Me (Developer):** Listen to refactoring suggestions
- **Both:** Prioritize clarity over shipping fast

### When to Refactor (Red Flags)

Stop and refactor if we notice:
- 🚩 Functions over 50 lines
- 🚩 Files over 500 lines
- 🚩 Code that needs explaining in chat to understand
- 🚩 Copy-pasted code with minor variations
- 🚩 Multiple ways to do the same thing
- 🚩 No clear error handling
- 🚩 Comments saying "TODO: fix this later"
- 🚩 Variable names like `data2`, `temp`, `x`

### Review Checkpoints

After completing a feature or module:
1. **Code Review:** Does this meet our standards?
2. **Refactor:** Clean up any rough spots NOW
3. **Document:** Update docs before moving on
4. **Test:** Verify it works as expected

Do NOT say "we'll clean it up later" - that almost never happens.

### What Production-Ready Means

Code that:
- ✅ Another expert developer can understand without asking questions
- ✅ Can be maintained 6 months from now
- ✅ Handles errors gracefully
- ✅ Has clear purpose and structure
- ✅ Uses standard patterns
- ✅ Won't embarrass me in a code review

### Code Review Questions to Ask

Before moving to the next feature:
- Can I explain this code in one sentence?
- Would another developer understand this?
- Are there any "clever" parts that could be simpler?
- Is error handling sufficient?
- Are there any code smells (duplication, long functions, etc.)?
- Is this documented well enough?

### Acceptable Trade-offs

**When speed matters more:**
- Quick scripts for one-time data processing
- Throwaway test code (that we delete after)
- Personal automation scripts

**Always maintain standards for:**
- Core application logic
- APIs and interfaces
- Database schemas
- User-facing features
- Anything that will be maintained long-term

### Communication Style

**When suggesting refactoring:**
- Be direct: "This is getting messy, let's refactor before adding more"
- Explain why: "This will be hard to debug if something breaks"
- Show better approach: "Here's a simpler pattern"

**When I notice issues:**
- Point them out immediately
- Don't let technical debt accumulate
- Suggest fixing now vs. later

## Example Dialogue

**Good:**
- Me: "Let's add user authentication"
- You: "Sure! I'll use a standard JWT approach with proper error handling. Here's the structure..."
- Me: "This auth code is getting complex, should we refactor?"
- You: "Yes, let's split it into separate modules: auth.py, tokens.py, middleware.py"

**Bad:**
- Me: "Let's add user authentication"
- You: "I'll hack together a quick auth system..."
- Me: "This is messy"
- You: "We'll rewrite it later"
- Me: (Never happens)

## Remember

**"Weeks of coding can save you hours of planning."** - Unknown

Good code is:
- **Boring** - Uses standard patterns
- **Obvious** - Clear what it does
- **Simple** - Easy to change
- **Documented** - Future-you will thank you

Great code is not:
- Clever
- Condensed
- Showing off
- Using every language feature

## Apply These Standards

Starting NOW, apply these standards to everything we build. If we're exploring and code gets messy, flag it and suggest cleaning up before proceeding.

**Question to ask me periodically:** "Should we refactor this before moving on?"

