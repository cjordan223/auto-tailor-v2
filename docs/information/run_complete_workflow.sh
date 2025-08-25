# # INFORMATION ONLY. THIS SCRIPT RESIDES IN RAYCAST SCRIPT SHARE. #
# #!/bin/bash
# # @raycast.schemaVersion 1
# # @raycast.title Complete Tex-Tailor Workflow
# # @raycast.mode silent
# # @raycast.packageName Tex-Tailor
# # @raycast.argument1 { "type": "text", "placeholder": "Enter job title" }
# # @raycast.argument2 { "type": "text", "placeholder": "Enter company name" }
# # @raycast.argument3 { "type": "text", "placeholder": "Provider (gemini/ollama/mistral/groq)", "optional": true }

# set -e

# # Colors for output
# RED='\033[0;31m'
# GREEN='\033[0;32m'
# YELLOW='\033[1;33m'
# BLUE='\033[0;34m'
# NC='\033[0m' # No Color        

# # Configuration
# PROJECT_DIR="/Users/connerjordan/Documents/Sandbox_v4"
# JD_REPO_DIR="$PROJECT_DIR/jd-repo"

# echo -e "${BLUE}🚀 Complete Tex-Tailor Workflow${NC}"
# echo -e "${BLUE}===============================${NC}"

# # Validate arguments
# JOB_TITLE="$1"
# COMPANY_NAME="$2"
# PROVIDER_ALIAS="$3"

# if [ -z "$JOB_TITLE" ]; then
#     echo -e "${RED}❌ Error: Job title must be provided as the first argument.${NC}"
#     exit 1
# fi

# if [ -z "$COMPANY_NAME" ]; then
#     echo -e "${RED}❌ Error: Company name must be provided as the second argument.${NC}"
#     exit 1
# fi

# # Provider mapping with recommended models
# if [ -z "$PROVIDER_ALIAS" ]; then
#     PROVIDER_ALIAS="gemini"
#     echo -e "${BLUE}📋 No provider specified, using default: Gemini${NC}"
# fi

# # Map provider aliases to actual providers and models
# case "$PROVIDER_ALIAS" in
#     "gemini"|"g")
#         PROVIDER="gemini"
#         MODEL="gemini-2.5-flash-lite"
#         echo -e "${BLUE}🤖 Using Gemini (${MODEL})${NC}"
#         ;;
#     "ollama"|"o")
#         PROVIDER="ollama"
#         MODEL="qwen2.5:14b-instruct"
#         echo -e "${BLUE}🤖 Using Ollama (${MODEL})${NC}"
#         ;;
#     "mistral"|"m")
#         PROVIDER="mistral"
#         MODEL="mistral-large-latest"
#         echo -e "${BLUE}🤖 Using Mistral (${MODEL})${NC}"
#         ;;
#     "groq"|"gq")
#         PROVIDER="groq"
#         MODEL="llama-3.1-70b-versatile"
#         echo -e "${BLUE}🤖 Using Groq (${MODEL})${NC}"
#         ;;
#     *)
#         echo -e "${RED}❌ Error: Invalid provider '$PROVIDER_ALIAS'. Valid options: gemini, ollama, mistral, groq${NC}"
#         echo -e "${YELLOW}   Using default: Gemini${NC}"
#         PROVIDER="gemini"
#         MODEL="gemini-2.5-flash-lite"
#         ;;
# esac

# # Get clipboard content
# JD_CONTENT=$(pbpaste)
# if [ -z "$JD_CONTENT" ]; then
#     echo -e "${RED}❌ Error: Clipboard is empty. Please copy the job description to your clipboard before running the script.${NC}"
#     exit 1
# fi

# # Check if jd-repo directory exists
# if [ ! -d "$JD_REPO_DIR" ]; then
#     echo -e "${RED}❌ Error: jd-repo directory not found at $JD_REPO_DIR${NC}"
#     exit 1
# fi

# # Check if frontend server is running
# if ! curl -s http://localhost:3001/api/providers > /dev/null 2>&1; then
#     echo -e "${RED}⚠️  Warning: Frontend server doesn't appear to be running on localhost:3001${NC}"
#     echo -e "${YELLOW}   Make sure to start it with: cd frontend && npm run dev${NC}"
# fi

# echo -e "${BLUE}📝 Step 1: Processing and saving job description...${NC}"

# # Function to clean and normalize text
# clean_text() {
#     sed 's/[[:space:]]*$//' | \
#     sed '/^[[:space:]]*$/d' | \
#     sed 's/["\"]//g' | \
#     sed "s/['']/'/g"
# }

# # Clean the content
# JD_CONTENT=$(echo "$JD_CONTENT" | clean_text)

# # Generate filename with custom timestamp format: MM_DDYY_HHMM_JOBTITLE
# FILENAME="$(date +"%m%d%y_%H%M")_${JOB_TITLE// /_}"
# FULL_PATH="$JD_REPO_DIR/${FILENAME}.txt"

# # Write the cleaned content with metadata
# {
#   echo "job_title: $JOB_TITLE"
#   echo "company: $COMPANY_NAME"
#   echo ""
#   echo "$JD_CONTENT"
# } > "$FULL_PATH"

# echo -e "${GREEN}✅ JD saved: ${FILENAME}.txt ($(wc -w < "$FULL_PATH") words)${NC}"

# echo -e "${BLUE}⚙️  Step 2: Running tex-tailor workflow via API...${NC}"

# # Activate virtual environment
# if [ ! -d "$PROJECT_DIR/venv" ]; then
#     echo -e "${RED}❌ Error: Python virtual environment not found at $PROJECT_DIR/venv/${NC}"
#     exit 1
# fi

# source "$PROJECT_DIR/venv/bin/activate"

# # Submit job to frontend API with provider settings and capture the response
# API_RESPONSE=$(curl -s -X POST http://localhost:3001/api/process \
#     -F "jobDescription=@$FULL_PATH" \
#     -F "provider=$PROVIDER" \
#     -F "model=$MODEL" \
#     -F "personality=career_savvy_colleague" \
#     -H "Content-Type: multipart/form-data")

# if [ $? -eq 0 ]; then
#     # Extract job ID from the response using basic text processing
#     JOB_ID=$(echo "$API_RESPONSE" | grep -o '"jobId":"[^"]*"' | cut -d'"' -f4)
    
#     if [ -n "$JOB_ID" ]; then
#         echo -e "${GREEN}✅ Workflow submitted successfully (Job ID: $JOB_ID)${NC}"
        
#         # Wait for the workflow to complete with progress indicators
#         echo -e "${BLUE}⏳ Waiting for workflow to complete...${NC}"
#         DOTS=""
#         while true; do
#             STATUS_RESPONSE=$(curl -s "http://localhost:3001/api/status/$JOB_ID")
#             STATUS=$(echo "$STATUS_RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
            
#             if [ "$STATUS" = "completed" ]; then
#                 echo -e "\n${GREEN}✅ Workflow completed successfully!${NC}"
#                 break
#             elif [ "$STATUS" = "failed" ] || [ "$STATUS" = "error" ]; then
#                 echo -e "\n${RED}❌ Workflow failed with status: $STATUS${NC}"
#                 deactivate
#                 exit 1
#             fi
            
#             # Show progress
#             DOTS="${DOTS}."
#             if [ ${#DOTS} -gt 3 ]; then
#                 DOTS=""
#             fi
#             printf "\r${BLUE}⏳ Processing${DOTS}   ${NC}"
            
#             sleep 2
#         done
        
#         RESULTS_URL="http://localhost:3000/results/$JOB_ID"
#         echo -e "${BLUE}🌐 Opening results page: $RESULTS_URL${NC}"
#         open "$RESULTS_URL"
        
#         echo -e "${GREEN}🎉 Complete workflow finished successfully!${NC}"
#         echo -e "${BLUE}📊 Job: $JOB_TITLE at $COMPANY_NAME${NC}"
#         echo -e "${BLUE}🤖 Provider: $PROVIDER ($MODEL)${NC}"
#     else
#         echo -e "${RED}❌ Could not extract job ID from API response${NC}"
#         deactivate
#         exit 1
#     fi
# else
#     echo -e "${RED}❌ Failed to submit workflow to API${NC}"
#     deactivate
#     exit 1
# fi

# # Deactivate virtual environment
# deactivate
