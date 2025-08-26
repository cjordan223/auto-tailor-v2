#!/bin/bash

echo "🧪 Testing LaTeX Compilation Locally"
echo "===================================="

# Activate Python virtual environment
source venv/bin/activate

# Test basic LaTeX compilation
echo "📄 Testing basic LaTeX compilation..."
cd frontend/temp
mkdir -p test_latex
cd test_latex

# Create a simple test LaTeX file
cat > test.tex << 'EOF'
\documentclass{article}
\usepackage{fontawesome5}
\usepackage{CormorantGaramond}
\usepackage{charter}

\begin{document}
\title{Test Document}
\author{Test Author}
\maketitle

\section{Introduction}
This is a test document to verify LaTeX compilation works locally.

\section{Features}
\begin{itemize}
    \item Basic LaTeX compilation
    \item FontAwesome icons: \faIcon{github}
    \item Custom fonts
    \item PDF generation
\end{itemize}

\end{document}
EOF

echo "📝 Created test.tex file"

# Try to compile it
echo "🔨 Compiling test.tex..."
if latexmk -pdf test.tex; then
    echo "✅ LaTeX compilation successful!"
    echo "📄 Generated test.pdf"
    ls -la *.pdf
else
    echo "❌ LaTeX compilation failed"
    echo "Check the error messages above"
    exit 1
fi

# Clean up
echo "🧹 Cleaning up test files..."
rm -f test.aux test.log test.fls test.fdb_latexmk test.out test.toc

echo ""
echo "🎉 LaTeX compilation test completed successfully!"
echo "Your local environment is ready for development."
