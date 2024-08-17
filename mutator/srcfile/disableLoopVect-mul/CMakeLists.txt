set(LLVM_LINK_COMPONENTS support)

add_clang_executable(disableLoopVect-mul
  disableLoopVect-mul.cpp
  )
target_link_libraries(disableLoopVect-mul
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