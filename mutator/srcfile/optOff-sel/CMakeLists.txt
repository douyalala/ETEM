set(LLVM_LINK_COMPONENTS support)

add_clang_executable(optOff-sel
  optOff-sel.cpp
  )
target_link_libraries(optOff-sel
  PRIVATE
  clangAST
  clangASTMatchers
  clangBasic
  clangFrontend
  clangSerialization
  clangTooling
  clangDriver
  clangRewrite
  clangRewriteFrontend
  clangStaticAnalyzerFrontend
  clangToolingSyntax
  )