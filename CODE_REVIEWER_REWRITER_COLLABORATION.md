# Code Reviewer ↔ Code Rewriter Collaboration Workflow

## Overview

The **Code Reviewer** and **Code Rewriter** agents work together in a sophisticated collaboration workflow where the reviewer creates structured task lists for the rewriter to fix systematically.

## 🔄 Collaboration Process

### Step 1: Code Review Analysis

The **Code Reviewer** conducts comprehensive AI-powered analysis:

```python
def handle_code_review_task(self, task):
    # 1. Uses AI with full project context
    # 2. Analyzes code quality, bugs, security, performance
    # 3. Creates structured review report
    # 4. Automatically delegates issues to Code Rewriter
```

#### Review Report Structure
```python
{
    "issues_found": 5,
    "issues": [
        {
            "severity": "CRITICAL",
            "description": "SQL injection vulnerability in user input",
            "file": "src/database.py", 
            "line_number": 42,
            "suggested_fix": "Use parameterized queries instead of string concatenation"
        },
        {
            "severity": "MAJOR",
            "description": "Memory leak in event handler",
            "file": "src/components/Timer.js",
            "line_number": 18,
            "suggested_fix": "Add cleanup in useEffect return function"
        },
        {
            "severity": "MINOR", 
            "description": "TODO comment needs completion",
            "file": "src/utils/helpers.js",
            "line_number": 7,
            "suggested_fix": "Implement the missing validation function"
        }
    ],
    "summary": "Found 5 issues requiring attention",
    "timestamp": "2025-11-03T10:30:00Z"
}
```

### Step 2: Structured Task Delegation

When issues are found, the **Code Reviewer** automatically creates structured tasks:

```python
def delegate_to_code_rewriter(self, review_result):
    # Creates detailed task with:
    # - Complete issue list with locations and fixes
    # - Severity breakdown (critical/major/minor counts)
    # - Metadata for tracking and follow-up
    
    task_id = self.comm.create_task(
        description=f"Fix {len(issues)} code issues from review report",
        task_type="code_rewrite_from_review",
        assigned_to="code_rewriter",
        metadata={
            "review_report": review_result,
            "total_issues": len(issues),
            "critical_issues": critical_count,
            "major_issues": major_count, 
            "minor_issues": minor_count
        }
    )
```

### Step 3: Systematic Issue Resolution

The **Code Rewriter** processes each issue systematically:

```python
def process_review_based_fixes(self, task):
    issues = task["metadata"]["review_report"]["issues"]
    
    for issue in issues:
        # 1. Analyze specific issue with AI
        # 2. Generate targeted fix
        # 3. Validate fix quality
        # 4. Apply to actual file with backup
        # 5. Update project context
        fix_result = self.apply_single_issue_fix(issue)
```

#### Individual Fix Process
```python
def apply_single_issue_fix(self, issue):
    # 1. Get current file content
    # 2. Create AI input for specific fix
    # 3. Generate enhanced content
    # 4. Validate fix addresses the issue
    # 5. Apply to file with backup
    # 6. Update cached project content
```

### Step 4: Results Tracking & Follow-up

The **Code Rewriter** provides detailed results:

```python
{
    "status": "completed",
    "total_issues": 5,
    "fixed_issues": 4,
    "failed_fixes": 1, 
    "fixed_details": [...],  # Successfully fixed issues
    "failed_details": [...], # Issues that couldn't be fixed
    "message": "Code rewriter completed: 4/5 issues fixed"
}
```

### Step 5: Automatic Follow-up

For failed fixes, the system automatically creates follow-up tasks:

```python
def request_review_follow_up(self, failed_fixes):
    # Creates high-priority task back to code reviewer
    # Includes details of what couldn't be fixed
    # Enables iterative improvement cycles
```

## 🎯 Key Features

### 1. **Structured Issue Lists**
- Each issue has specific file location and line number
- Severity categorization (Critical/Major/Minor)
- Suggested fix approach for each problem
- Complete context for targeted resolution

### 2. **AI-Powered Analysis**
The Code Reviewer uses standardized AI input:
```python
standardized_input = self.create_standardized_ai_input(
    operation_type="CODE_REVIEW",
    task_description="Comprehensive code review",
    context_type="QUALITY_ANALYSIS",
    requirements=[
        "Analyze code quality and best practices",
        "Identify bugs, security issues, performance problems",
        "Check maintainability and readability",
        "Verify error handling and edge cases"
    ],
    constraints=[
        "Provide specific line numbers and file locations",
        "Categorize by severity (critical, major, minor)", 
        "Suggest specific fixes for each issue",
        "Include positive feedback for good code"
    ]
)
```

### 3. **Targeted Fix Generation**
The Code Rewriter creates AI input for each specific issue:
```python
standardized_input = self.create_standardized_ai_input(
    operation_type="ISSUE_FIX",
    task_description=f"Fix {severity} issue: {description}",
    context_type="CODE_REPAIR",
    requirements=[
        f"Target file: {file_path}",
        f"Line number: {line_number}",
        f"Suggested approach: {suggested_fix}",
        "Maintain all existing functionality"
    ],
    constraints=[
        "Make minimal necessary changes",
        "Preserve existing code structure",
        "Ensure fix doesn't introduce new issues"
    ]
)
```

### 4. **Safe File Operations**
- Automatic file backups before modifications
- Validation of fix quality before applying
- Project context updates after successful fixes
- Rollback capability if issues occur

### 5. **Progress Tracking**
- Real-time status updates during fix processing
- Detailed reporting of success/failure rates
- Metadata tracking for audit and follow-up
- Automatic escalation for failed fixes

## 📋 Example Workflow

### User Command:
```bash
delegate "review TimeDisplayApp for code quality and fix all issues" to code_reviewer
```

### System Execution:

1. **Code Reviewer** conducts analysis:
   ```
   🔍 CODE REVIEWER: Conducting comprehensive code review
   📋 Found 3 issues requiring attention:
      🚨 CRITICAL: Security vulnerability in auth.js:15
      ⚠️ MAJOR: Memory leak in Timer.js:42
      ℹ️ MINOR: TODO item in utils.js:7
   🔄 Delegating 3 issues to code rewriter
   ```

2. **Code Rewriter** processes fixes:
   ```
   🔧 CODE REWRITER: Processing code fixes
   🔨 Fixing issue 1/3: CRITICAL - Security vulnerability
      ✅ Fixed: auth.js (backup: auth.js.backup)
   🔨 Fixing issue 2/3: MAJOR - Memory leak
      ✅ Fixed: Timer.js (backup: Timer.js.backup)  
   🔨 Fixing issue 3/3: MINOR - TODO completion
      ✅ Fixed: utils.js (backup: utils.js.backup)
   📊 REWRITE SUMMARY: 3/3 issues fixed
   ```

3. **Final Result**:
   ```
   ✅ All critical and major issues resolved
   💾 Original files backed up safely
   📊 Project quality significantly improved
   ```

## 🔧 Integration Benefits

### 1. **Automated Quality Assurance**
- No manual issue tracking needed
- Systematic resolution of all problems
- Consistent application of fixes

### 2. **AI-Powered Intelligence**
- Context-aware issue detection
- Smart fix generation based on project patterns
- Maintains code consistency and style

### 3. **Scalable Collaboration**
- Handles projects of any size
- Processes multiple issues in parallel
- Extensible to additional quality checks

### 4. **Audit Trail**
- Complete record of all issues found and fixed
- Backup files for rollback capability
- Detailed reporting for project management

## 🚀 Usage Examples

### React Project Code Review:
```bash
delegate "review React components for performance and best practices" to code_reviewer
# → Reviewer finds prop validation issues, unused imports, optimization opportunities
# → Rewriter automatically fixes all identified issues with modern React patterns
```

### Python API Security Review:
```bash
delegate "security audit of Python API endpoints" to code_reviewer  
# → Reviewer identifies SQL injection risks, authentication bypasses, data validation gaps
# → Rewriter implements parameterized queries, proper auth checks, input validation
```

### Full Stack Quality Assessment:
```bash  
delegate "comprehensive code quality review of entire application" to code_reviewer
# → Reviewer analyzes frontend, backend, database interactions, configuration
# → Rewriter systematically fixes all issues across technology stack
```

---

**The Code Reviewer → Code Rewriter collaboration creates a powerful automated quality assurance pipeline that systematically identifies and resolves code issues using AI-powered analysis and structured task delegation.**