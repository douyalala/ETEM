set(LLVM_LINK_COMPONENTS support)

add_clang_executable(addGoto-sel
  addGoto-sel.cpp
  )
target_link_libraries(addGoto-sel
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