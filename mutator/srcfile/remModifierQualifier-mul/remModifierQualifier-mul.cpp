//------------------------------------------------------------------------------
// mutate strategy: remove modifier
// inputs: targeted modifier
// usage: remModifierQualifier-mul <path to main.c> --  <targeted modifier> <position>
//------------------------------------------------------------------------------
#include <sstream>
#include <string>
#include <iostream>
#include <fstream>
#include <memory>
#include <map>
#include <vector>
#include "clang/AST/AST.h"
#include "clang/AST/ASTConsumer.h"
#include "clang/AST/RecursiveASTVisitor.h"
#include "clang/Frontend/ASTConsumers.h"
#include "clang/Frontend/FrontendActions.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Tooling/CommonOptionsParser.h"
#include "clang/Tooling/Tooling.h"
#include "clang/Rewrite/Core/Rewriter.h"
#include "llvm/Support/raw_ostream.h"
#include "clang/Lex/Lexer.h"
using namespace std;
using namespace clang;
using namespace clang::driver;
using namespace clang::tooling;

static llvm::cl::OptionCategory VisitAST_Category("usage: remModifierQualifier-mul <path to main.c> --  <targeted modifier> <position>");
static string mutateType = "";
static int64_t position = -1;

// By implementing RecursiveASTVisitor, we can specify which AST nodes
// we're interested in by overriding relevant methods.
class MyASTVisitor : public RecursiveASTVisitor<MyASTVisitor> {
public:
  ASTContext *Context=NULL;
  MyASTVisitor(Rewriter &R) : TheRewriter(R) {}
  LangOptions lopt;
  string decl2str(VarDecl *d) {
    SourceLocation b(d->getSourceRange().getBegin()), _e(d->getSourceRange().getEnd());
    SourceLocation e(Lexer::getLocForEndOfToken(_e, 0, TheRewriter.getSourceMgr(), lopt));
    return string(TheRewriter.getSourceMgr().getCharacterData(b),
        TheRewriter.getSourceMgr().getCharacterData(e)-TheRewriter.getSourceMgr().getCharacterData(b));
  }

  bool VisitVarDecl(VarDecl *d) {
    if(d->getID()!=position) return true;

    cout<<"mutate here"<<endl;

    string oristr = decl2str(d);
    string identifier = mutateType;
    string inttype = "int";
    string chartype = "char";
    string shorttype = "short";
    string longtype = "long";
    string unsignedtype = "unsigned";
    string vartype = d->getType().getAsString();

    string newstr = "";

    if(strcmp(mutateType.c_str(),"unsigned")==0) {
      if(oristr.find(inttype) != string::npos
          || oristr.find(chartype) != string::npos
          || oristr.find(shorttype) != string::npos
          || oristr.find(longtype) != string::npos){
        // remove
        int pos = oristr.find(identifier);
        newstr = oristr.replace(pos,8+1,"");
        cout<<"remove: "<<newstr<<endl;
      } else {
        // replace: identifier->int
          int pos = oristr.find(identifier);
          newstr = oristr.replace(pos,8,inttype);
          cout<<"replace: "<<newstr<<endl;
      } 
    } else if(strcmp(mutateType.c_str(),"signed")==0) {
      if(oristr.find(inttype) != string::npos
          || oristr.find(chartype) != string::npos
          || oristr.find(shorttype) != string::npos
          || oristr.find(longtype) != string::npos){
        // remove
        int pos = oristr.find(identifier);
        newstr = oristr.replace(pos,6+1,"");
        cout<<"remove: "<<newstr<<endl;
      } else {
        // replace
        int pos = oristr.find(identifier);
        newstr = oristr.replace(pos,6,inttype);
        cout<<"replace: "<<newstr<<endl;
      } 
    } else if(strcmp(mutateType.c_str(),"short")==0) {
      if(oristr.find(inttype) != string::npos){
          int pos = oristr.find(identifier);
          newstr = oristr.replace(pos,5+1,"");
          cout<<"remove: "<<newstr<<endl;
      } else {
          int pos = oristr.find(identifier);
          newstr = oristr.replace(pos,5,inttype);
          cout<<"replace: "<<newstr<<endl;
      } 
    } else if(strcmp(mutateType.c_str(),"long")==0) {
      if(oristr.find(inttype) != string::npos){
          int pos = oristr.find(identifier);
          newstr = oristr.replace(pos,4+1,"");
          cout<<"remove: "<<newstr<<endl;
      } else {
          int pos = oristr.find(identifier);
          newstr = oristr.replace(pos,4,inttype);
          cout<<"replace: "<<newstr<<endl;
      } 
    } else if(strcmp(mutateType.c_str(),"const")==0) {
      int pos = vartype.find(identifier);
      string orivartypr = vartype;
      newstr = vartype.replace(pos,5+1,"");
      cout<<"remove: "<<newstr<<endl;
    } else if(strcmp(mutateType.c_str(),"restrict")==0) {
      int pos = vartype.find(identifier);
      string orivartypr = vartype;
      newstr = vartype.replace(pos,8+1,"");
      cout<<"remove: "<<newstr<<endl;
    } else if(strcmp(mutateType.c_str(),"volatile")==0) {
      int pos = vartype.find(identifier);
      string orivartypr = vartype;
      newstr = vartype.replace(pos,8+1,"");
      cout<<"remove: "<<newstr<<endl;
    }
    
    TheRewriter.ReplaceText(d->getSourceRange(),newstr);

    return false;
  }

private:
  Rewriter &TheRewriter;
};

// Implementation of the ASTConsumer interface for reading an AST produced
// by the Clang parser.
class MyASTConsumer : public ASTConsumer {
public:
  MyASTConsumer(Rewriter &R) : Visitor(R) {}

  void HandleTranslationUnit(ASTContext &Context) override {
    /* we can use ASTContext to get the TranslationUnitDecl, which is
       a single Decl that collectively represents the entire source file */
    Visitor.Context=&Context;
    Visitor.TraverseDecl(Context.getTranslationUnitDecl());
  }

private:
  MyASTVisitor Visitor;
};

// For each source file provided to the tool, a new FrontendAction is created.
class MyFrontendAction : public ASTFrontendAction {
public:
  MyFrontendAction() {}

  int CopyFile(char *SourceFile,char *NewFile) 
  {  
    ifstream in; 
    ofstream out;  
    in.open(SourceFile,ios::binary);//
    if(in.fail())//
    {     
        cout<<"Error 1: Fail to open the source file."<<endl;    
        in.close();    
        out.close();    
        return 0; 
    }  
    out.open(NewFile,ios::binary);//
    if(out.fail())//
    {     
        cout<<"Error 2: Fail to create the new file."<<endl;    
        out.close();    
        in.close();    
        return 0; 
    }  
    else//
    {     
        out<<in.rdbuf();    
        out.close();    
        in.close();    
        return 1; 
    } 
  }

  void EndSourceFileAction() override {
    SourceManager &SM = TheRewriter.getSourceMgr();
    llvm::errs() << "** EndSourceFileAction for: "
                 << SM.getFileEntryForID(SM.getMainFileID())->getName() << "\n";

    // Now emit the rewritten buffer.
    CopyFile("main.c", "mainori.c");
    TheRewriter.overwriteChangedFiles();
    rename("main.c", "mainvar.c");
    rename("mainori.c", "main.c");
  }

  std::unique_ptr<ASTConsumer> CreateASTConsumer(CompilerInstance &CI,
                                                 StringRef file) override {
    llvm::errs() << "** Creating AST consumer for: " << file << "\n";
    TheRewriter.setSourceMgr(CI.getSourceManager(), CI.getLangOpts());
    return make_unique<MyASTConsumer>(TheRewriter);
  }

private:
  Rewriter TheRewriter;
};

int main(int argc, const char **argv) {
  mutateType = argv[3];
  position = atol(argv[4]);

  cout<<"-- running: remModifierQualifier-mul"<<endl;
  cout<<"---- mutateType: "<<mutateType<<endl;
  cout<<"---- position: "<<position<<endl;

  llvm::Expected<clang::tooling::CommonOptionsParser> OptionsParser=CommonOptionsParser::create(argc, argv, VisitAST_Category);
  ClangTool Tool(OptionsParser->getCompilations(), OptionsParser->getSourcePathList());

  Tool.run(newFrontendActionFactory<MyFrontendAction>().get());

  return 0;
}
