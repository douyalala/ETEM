set(LLVM_LINK_COMPONENTS support)

add_clang_executable(disableLoopVect-sel
  disableLoopVect-sel.cpp
  )
target_link_libraries(disableLoopVect-sel
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